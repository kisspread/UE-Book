# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（ML 模型数据、纹理合成模型、PCA 模型） |
| 模块 | `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTechLib 是 MetaHuman 生态系统的**底层计算引擎**，为 MetaHuman Creator（云端角色创建工具）和 MetaHuman Animator（面部动捕驱动工具）提供核心算法支持。

该插件解决的核心问题包括：

1. **面部身份拟合（Face Conforming）**：从 3D 扫描数据或深度图 + 2D 关键点数据，将通用面部模板拟合为特定人物的面部网格，生成 DNA 数据
2. **身体身份建模（Body Identity）**：基于 PCA 模型对身体进行参数化建模，支持从网格拟合、骨骼比例混合、身体约束等操作
3. **面部纹理合成（Texture Synthesis）**：基于 ML 模型，根据 UV 坐标和高频索引参数化生成面部反照率贴图和法线贴图
4. **DNA 数据读写**：提供 `dna::BinaryStreamReader` 的 UE 包装层，统一访问面部/身体的几何、行为、动画数据
5. **网格工具函数**：UV 最近邻查找、邻接顶点计算、关节世界坐标提取等底层几何操作

**为什么需要手动启用**：该插件包含大量第三方 ML 推理库和预训练模型数据，体积较大，且主要被 MetaHuman Creator / Animator 插件内部依赖，普通项目通常不需要直接使用。

## 使用场景

- 你在开发 MetaHuman 相关工具链，需要底层的面部/身体拟合算法 → 使用 `FMetaHumanConformer` 进行身份拟合
- 你需要从扫描数据生成 MetaHuman DNA → 使用 `FMetaHumanConformer::FitIdentity` + `FitTeeth`
- 你需要对 MetaHuman 身体进行参数化混合 → 使用 `FMetaHumanCharacterBodyIdentity` 的 PCA 模型
- 你需要程序化生成面部纹理 → 使用 `FMetaHumanFaceTextureSynthesizer`
- 你需要读取和操作 DNA 资产数据 → 使用 `FReader` 包装类或 `IDNAReader` 接口

## 蓝图用法

该插件主要面向 C++ 层，蓝图暴露有限。以下是可在蓝图中使用的类型和枚举：

### 核心枚举

| 枚举 | 说明 | 所在头文件 |
|---|---|---|
| `EIdentityErrorCode` | 面部拟合过程中的错误码（None、MLRig、FitRigid、FitPCA 等） | `MetaHumanIdentityErrorCode.h` |
| `EAutoRigIdentityValidationError` | 自动绑定身份验证错误码 | `MetaHumanIdentityErrorCode.h` |
| `EBodyBlendOptions` | 身体混合模式：仅骨骼比例 / 仅塑形 / 两者兼有 | `MetaHumanCharacterBodyIdentity.h` |
| `EMetaHumanCharacterBodyFitOptions` | 身体拟合选项：仅网格 / 网格+骨骼 / 网格到固定骨骼 | `MetaHumanCharacterBodyIdentity.h` |
| `EAlignmentOptions` | 头部对齐选项：无 / 平移 / 旋转+平移 / 缩放+平移 / 全部 | `MetaHumanCharacterIdentity.h` |
| `EBlendOptions` | 面部混合选项：比例 / 特征 / 两者兼有 | `MetaHumanCharacterIdentity.h` |

### 蓝图结构体

| 结构体 | 说明 | 所在头文件 |
|---|---|---|
| `FConformBodyParams` | 身体拟合参数（是否导入辅助关节、目标是否为 A-pose 等） | `MetaHumanCharacterBodyIdentity.h` |
| `FMetaHumanCharacterBodyConstraint` | 身体约束（名称、激活状态、目标测量值、最小/最大值） | `MetaHumanCharacterBodyIdentity.h` |
| `FFitToTargetOptions` | 面部拟合到目标的选项（对齐方式、是否禁用高频细节） | `MetaHumanCharacterIdentity.h` |

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConformer.h"
#include "MetaHumanCharacterIdentity.h"
#include "MetaHumanCharacterBodyIdentity.h"
#include "MetaHumanFaceTextureSynthesizer.h"
#include "MetaHumanCoreTechMeshUtils.h"
#include "MetaHumanCoreTechLibVersion.h"
```

### 基本用法：面部身份拟合

从扫描数据拟合面部身份，生成顶点数据：

```cpp
// 来源: MetaHumanConformer.h
#include "MetaHumanConformer.h"

using namespace UE::Wrappers;

// 1. 创建 Conformer 并初始化
FMetaHumanConformer Conformer;
bool bSuccess = Conformer.Init(
    TemplateDescriptionJson,   // 模板描述 JSON
    IdentityModelJson,         // 身份模型 JSON（DNA 数据库描述）
    FittingConfigurationJson   // 拟合配置 JSON
);

// 2. 设置相机参数
TArray<FCameraCalibration> Calibrations;
// ... 填充相机标定数据
Conformer.SetCameras(Calibrations);

// 3. 设置输入数据（二选一：扫描 或 深度图）
// 方式 A：3D 扫描数据
bool bInvalidTopology = false;
Conformer.SetScanInputData(
    Landmarks2DData,    // 每个相机的 2D 关键点
    Landmarks3DData,    // 3D 关键点
    Triangles,          // 三角面索引 (numTriangles x 3)
    Vertices,           // 顶点位置 (numVertices x 3)
    bInvalidTopology
);

// 方式 B：深度图数据
// Conformer.SetDepthInputData(LandmarksDataPerCamera, DepthMaps);

// 4. 执行拟合
TArray<float> FaceVertices, LeftEyeVertices, RightEyeVertices;
TArray<float> StackedTransforms, StackedScales;
EIdentityErrorCode ErrorCode = Conformer.FitIdentity(
    FaceVertices, LeftEyeVertices, RightEyeVertices,
    StackedTransforms, StackedScales,
    true  // bFitEyes
);

if (ErrorCode == EIdentityErrorCode::None)
{
    // 拟合成功，FaceVertices 包含 numVertices x 3 的列主序顶点数据
}

// 5. 拟合牙齿
TArray<float> TeethVertices;
Conformer.FitTeeth(TeethVertices);
```

### 基本用法：身体身份建模

```cpp
// 来源: MetaHumanCharacterBodyIdentity.h
#include "MetaHumanCharacterBodyIdentity.h"

// 1. 初始化身体身份模型
FMetaHumanCharacterBodyIdentity BodyIdentity;
BodyIdentity.Init(PCAModelPath, LegacyBodiesPath);

// 2. 获取 LOD0 顶点数
int32 NumVertices = BodyIdentity.GetNumLOD0MeshVertices(false); // false = body only
int32 NumCombinedVertices = BodyIdentity.GetNumLOD0MeshVertices(true); // true = combined

// 3. 创建状态并进行混合操作
TSharedPtr<FMetaHumanCharacterBodyIdentity::FState> BodyState = BodyIdentity.CreateState();
// BodyState 提供混合、拟合等操作（具体方法在 FState 类中）
```

### 基本用法：面部纹理合成

```cpp
// 来源: MetaHumanFaceTextureSynthesizer.h
#include "MetaHumanFaceTextureSynthesizer.h"

// 1. 创建并初始化纹理合成器
FMetaHumanFaceTextureSynthesizer Synthesizer;
bool bSuccess = Synthesizer.Init(TextureSynthesisFolderPath, 4); // 4 线程

if (Synthesizer.IsValid())
{
    // 2. 查询支持的贴图类型
    TArray<FMetaHumanFaceTextureSynthesizer::EMapType> AlbedoTypes = 
        Synthesizer.GetSupportedAlbedoMapTypes();
    TArray<FMetaHumanFaceTextureSynthesizer::EMapType> NormalTypes = 
        Synthesizer.GetSupportedNormalMapTypes();

    // 3. 设置合成参数
    FMetaHumanFaceTextureSynthesizer::FTextureSynthesisParams Params;
    Params.SkinUVFromUI = FVector2f(0.5f, 0.3f);  // UV 皮肤坐标
    Params.HighFrequencyIndex = 0;                   // 高频细节索引
    Params.MapType = FMetaHumanFaceTextureSynthesizer::EMapType::Base;

    // 4. 合成纹理（具体合成方法在 Synthesize 系列函数中）
    int32 MaxHFIndex = Synthesizer.GetMaxHighFrequencyIndex();
    int32 SizeX = Synthesizer.GetTextureSizeX();
    int32 SizeY = Synthesizer.GetTextureSizeY();
}

// 5. 使用完毕后释放资源
Synthesizer.Clear();
```

### 基本用法：网格工具函数

```cpp
// 来源: MetaHumanCoreTechMeshUtils.h
#include "MetaHumanCoreTechMeshUtils.h"

using namespace UE::MetaHuman;

// 1. UV 最近邻查找
TArray<FVector2f> MeshUVs;   // 网格 UV 坐标
TArray<FVector2f> InputUVs;  // 查询 UV 坐标
TArray<TPair<int32, float>> ClosestUVs = GetClosestUVIndices(MeshUVs, InputUVs);
// ClosestUVs[i].Key = 最近邻索引, ClosestUVs[i].Value = UV 空间距离

// 2. 获取邻接顶点
TSharedPtr<IDNAReader> DNAReader;
TMap<int32, TArray<int32>> Neighbours = GetNeighbouringVertices(
    DNAReader, DNAMeshIndex, VertexIds
);

// 3. 获取关节世界坐标
TArray<FVector3f> JointTranslations = GetJointWorldTranslations(DNAReader);
```

### 进阶用法：DNA 数据读取

```cpp
// 来源: FReader.h
#include "FReader.h"
#include "DNAAsset.h"

// 使用 FReader 包装 UDNAAsset，通过 dna::BinaryStreamReader 接口访问数据
UDNAAsset* DNAAsset = /* 获取 DNA 资产 */;
dna::FReader Reader(DNAAsset);

// 访问几何数据
uint32 VertCount = Reader.getVertexPositionCount(0); // meshIndex = 0
auto Xs = Reader.getVertexPositionXs(0);
auto Ys = Reader.getVertexPositionYs(0);
auto Zs = Reader.getVertexPositionZs(0);

// 访问行为数据
uint16 GUIControlCount = Reader.getGUIControlCount();
for (uint16 i = 0; i < GUIControlCount; ++i)
{
    dna::StringView Name = Reader.getGUIControlName(i);
}

// 访问关节数据
uint16 JointCount = Reader.getJointCount();
for (uint16 i = 0; i < JointCount; ++i)
{
    dna::StringView JointName = Reader.getJointName(i);
}

// 访问混合变形数据
uint16 BlendShapeCount = Reader.getBlendShapeTargetCount(0);
```

### 进阶用法：面部身份混合与拟合

```cpp
// 来源: MetaHumanCharacterIdentity.h
#include "MetaHumanCharacterIdentity.h"

// 1. 初始化面部身份
FMetaHumanCharacterIdentity FaceIdentity;
FaceIdentity.Init(MHCDataPath, BodyMHCDataPath, DNAAsset, 
                  EMetaHumanCharacterOrientation::Y_UP);

// 2. 获取预设列表
TArray<FString> PresetNames = FaceIdentity.GetPresetNames();

// 3. 创建状态进行混合操作
TSharedPtr<FMetaHumanCharacterIdentity::FState> FaceState = FaceIdentity.CreateState();

// 4. 获取 LOD0 顶点数
int32 HeadVerts = FaceIdentity.GetNumLOD0MeshVertices(EHeadFitToTargetMeshes::Head);
int32 LeftEyeVerts = FaceIdentity.GetNumLOD0MeshVertices(EHeadFitToTargetMeshes::LeftEye);
int32 RightEyeVerts = FaceIdentity.GetNumLOD0MeshVertices(EHeadFitToTargetMeshes::RightEye);
int32 TeethVerts = FaceIdentity.GetNumLOD0MeshVertices(EHeadFitToTargetMeshes::Teeth);

// 5. 从身体复制关节绑定姿态到面部
TSharedPtr<IDNAReader> UpdatedFaceReader = 
    FaceIdentity.CopyBodyJointsToFace(BodyDnaReader, FaceDnaReader, true);

// 6. 从身体和顶点法线更新面部蒙皮权重
TArray<TPair<int32, TArray<FFloatTriplet>>> CombinedBodySkinWeights;
TSharedPtr<IDNAReader> UpdatedReader = 
    FaceIdentity.UpdateFaceSkinWeightsFromBodyAndVertexNormals(
        CombinedBodySkinWeights, FaceDnaReader, *FaceState);
```

## Demo 示例

以下示例展示如何初始化面部 Conformer 并执行一次基本的身份拟合流程：

```cpp
// MetaHumanConformerDemo.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanConformerDemo
{
public:
    /** 从扫描数据拟合面部身份 */
    static bool FitFaceFromScan(
        const FString& InTemplateJson,
        const FString& InModelJson,
        const FString& InConfigJson,
        const TArray<int32>& InTriangles,
        const TArray<float>& InVertices,
        TArray<float>& OutFaceVertices
    );

    /** 获取 MetaHuman Core Tech Lib 版本 */
    static FString GetVersion();
};
```

```cpp
// MetaHumanConformerDemo.cpp
#include "MetaHumanConformerDemo.h"
#include "MetaHumanConformer.h"
#include "MetaHumanCoreTechLibVersion.h"
#include "MetaHumanIdentityErrorCode.h"

using namespace UE::Wrappers;

bool FMetaHumanConformerDemo::FitFaceFromScan(
    const FString& InTemplateJson,
    const FString& InModelJson,
    const FString& InConfigJson,
    const TArray<int32>& InTriangles,
    const TArray<float>& InVertices,
    TArray<float>& OutFaceVertices)
{
    // 创建并初始化 Conformer
    FMetaHumanConformer Conformer;
    if (!Conformer.Init(InTemplateJson, InModelJson, InConfigJson))
    {
        UE_LOG(LogMetaHumanCoreTechLib, Error, TEXT("Failed to initialize MetaHuman Conformer"));
        return false;
    }

    // 设置扫描输入数据（无关键点，简化示例）
    TSortedMap<FString, const FFrameTrackingContourData*> Landmarks2D;
    TSortedMap<FString, const FTrackingContour3D*> Landmarks3D;
    bool bInvalidTopology = false;

    if (!Conformer.SetScanInputData(Landmarks2D, Landmarks3D, InTriangles, InVertices, bInvalidTopology))
    {
        UE_LOG(LogMetaHumanCoreTechLib, Error, TEXT("Failed to set scan input data"));
        return false;
    }

    // 执行身份拟合
    TArray<float> LeftEyeVerts, RightEyeVerts, Transforms, Scales;
    EIdentityErrorCode ErrorCode = Conformer.FitIdentity(
        OutFaceVertices, LeftEyeVerts, RightEyeVerts,
        Transforms, Scales, false
    );

    if (ErrorCode != EIdentityErrorCode::None)
    {
        UE_LOG(LogMetaHumanCoreTechLib, Error, 
            TEXT("FitIdentity failed with error code: %d"), static_cast<int32>(ErrorCode));
        return false;
    }

    UE_LOG(LogMetaHumanCoreTechLib, Log, 
        TEXT("Face fitting succeeded. Output vertices: %d"), OutFaceVertices.Num() / 3);
    return true;
}

FString FMetaHumanConformerDemo::GetVersion()
{
    return FMetaHumanCoreTechLibVersion::GetMetaHumanCoreTechLibVersionString();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenCV` | 面部拟合中的图像处理和计算机视觉算法 |
| `OpenCVHelper` | OpenCV 与 UE 之间的数据转换辅助 |
| `OnlineSubsystem` | 云端 MetaHuman 服务通信 |
| `DirectoryWatcher` | 监控捕获数据文件夹变化 |
| `MetaHumanImageViewer` | 捕获数据的图像预览（插件内部模块） |

## 维护状态

### 近期更新

```
- aae1c3c9d847 Added joint orients to MHC bodies（为 MetaHuman 身体添加关节朝向数据）
- e60ff129d651 Added missing file for CL46712797（补充遗漏文件）
- b20650671b2e Removing set to a pose from metahuman body conform UI. Fixing bugs related to body conform.（移除身体拟合 UI 中的姿态设置，修复相关 bug）
```

### 维护评价

- **创建时间**：2025-01-20，插件非常新（约 6 个月）
- **更新频率**：近期有功能性更新（关节朝向、身体拟合 bug 修复），表明处于**活跃开发**阶段
- **实验性状态**：`IsBetaVersion=false`，`IsExperimentalVersion=false`，但 `EnabledByDefault=false`，说明该插件是正式功能但需要手动启用
- **代码规模**：605 个源文件，属于超大型插件，包含大量 ML 推理和几何计算代码
- **已知限制**：该插件主要作为 MetaHuman Creator / Animator 的内部依赖，直接使用需要较深的领域知识；依赖 OpenCV 和 OnlineSubsystem 等外部模块
- **推荐程度**：如果你在开发 MetaHuman 相关工具或需要面部/身体拟合能力，这是必选依赖；普通项目无需引入

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- 官方文档（无）