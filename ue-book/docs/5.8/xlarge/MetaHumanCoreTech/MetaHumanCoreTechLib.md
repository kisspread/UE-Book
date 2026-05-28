# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 核心技术 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（技术数据配置） |
| 模块 | `MetaHumanBodyTrackerInterface` (Runtime), `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-06-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 Epic Games MetaHuman 生态系统的**底层核心技术库**。它不是一个面向最终用户的插件，而是为 **MetaHuman Creator**（云端角色创建工具）和 **MetaHuman Animator**（面部动画捕捉工具）提供核心算法支撑。

该插件的核心能力包括：

1. **人脸身份拟合（Actor Creation）**：将扫描数据（3D 扫描、深度图、2D 关键点）拟合到 MetaHuman 面部模板，生成个性化面部身份。支持刚性对齐、非刚性 PCA 模型拟合、逐顶点精细拟合三个阶段。

2. **身体形状编辑（Body Shape Editor）**：基于 PCA 模型和 GUI 控制器编辑角色身体形状、骨骼比例、姿态，支持区域混合、预设选择、身体-面部接缝适配。

3. **面部形状编辑（MetaHuman Creator）**：基于 Patch Blend Model 的区域化面部编辑系统，支持表情、变异体、高频细节等参数化控制。

4. **骨骼变形（Rig Morphing）**：将编辑后的网格变化传递到 RigLogic 骨骼系统，更新关节位置、蒙皮权重、动画控制器。

5. **纹理合成（Texture Synthesis）**：根据面部形状生成对应的皮肤纹理（法线、腔体、反照率贴图）。

6. **Rig 评估（Evaluate Rig）**：评估 DNA 文件中的原始控制器以驱动网格变形。

7. **人脸追踪拟合（Face Fitting / Conformer）**：将模板面部网格逐步对齐到高分辨率 3D 扫描数据，支持 ICP 点云配准、关键点约束、碰撞检测等。

**为什么存在**：MetaHuman 技术栈的核心难题是将通用的参数化面部/身体模板适配到真实人类的扫描数据或动画捕捉数据。这个插件封装了所有底层几何优化、线性代数、PCA 模型、网格处理算法，使上层插件（MetaHuman Creator / Animator）可以专注于业务逻辑。

## 使用场景

- **MetaHuman Creator 工作流**：你在使用 MetaHuman Creator 创建角色时，面部和身体的形状编辑、预设混合、表情校准全部依赖此插件的 API。
- **MetaHuman Animator 工作流**：你在使用 iPhone 捕捉面部动画并应用到 MetaHuman 时，面部关键点拟合和表情参数化依赖此插件。
- **自定义角色创建管线**：你需要从 3D 扫描数据（如 iPhone LiDAR 或专业扫描仪）自动创建 MetaHuman 角色，使用 `ActorCreationAPI` 和 `MetaHumanCreatorAPI` 进行程序化拟合。
- **身体动画管线**：你需要程序化地编辑角色身体形状、混合预设、适配蒙皮权重。
- **Rig 变形和修改**：你需要程序化地修改 DNA 骨骼文件，调整关节位置、添加形状等。
- **测试和调试**：你需要评估 RigLogic 骨骼在不同控制器值下的网格输出。

## 蓝图用法

⚠️ **此插件主要提供 C++ API，不直接暴露蓝图节点**。`MetaHumanCoreTechLib` 模块的 API 均为 C++ 原生类（非 `UObject`/`UCLASS`），无法直接在蓝图中调用。如需在蓝图中使用 MetaHuman 功能，应使用上层的 **MetaHuman Creator** 和 **MetaHuman Animator** 插件提供的蓝图接口。

## C++ 用法

### 头文件引入

```cpp
// Actor Creation API
#include "api/ActorCreationAPI.h"

// Actor Refinement API
#include "api/ActorRefinementAPI.h"

// MetaHuman Creator Face API
#include "api/MetaHumanCreatorAPI.h"

// MetaHuman Creator Body API
#include "api/MetaHumanCreatorBodyAPI.h"

// Evaluate Rig API
#include "api/EvaluateRigAPI.h"

// Rig Morph Module
#include "rigmorpher/RigMorphModule.h"
```

### 基本用法 - Actor Creation（面部身份拟合）

从扫描数据拟合面部身份（来源：`Private/api/ActorCreationAPI.h`）：

```cpp
#include "api/ActorCreationAPI.h"

// 创建 Actor Creation API 实例
TITAN_API_NAMESPACE::ActorCreationAPI ActorCreator;

// 初始化（使用 JSON 配置）
if (!ActorCreator.Init("path/to/template_description.json",
                       "path/to/identity_model.json"))
{
    // 初始化失败
    return;
}

// 设置相机参数
std::map<std::string, OpenCVCamera> cameras;
// ... 填充相机数据
ActorCreator.SetCameras(cameras);

// 设置扫描输入数据（3D 扫描 + 关键点）
std::map<std::string, const TITAN_API_NAMESPACE::FaceTrackingLandmarkData> landmarks3D;
std::map<std::string, std::map<std::string, TITAN_API_NAMESPACE::FaceTrackingLandmarkData>> landmarks2D;
TITAN_API_NAMESPACE::MeshInputData scanData;
bool bInvalidTopology = false;
ActorCreator.SetScanInputData(landmarks3D, landmarks2D, scanData, bInvalidTopology);

// 第一阶段：刚性拟合（对齐模板到扫描）
float vertexPositions[/* numVertices x 3 */];
float transforms[/* numFrames x 16 */]; // 4x4 矩阵
float scales[/* numFrames */];
ActorCreator.FitRigid(vertexPositions, transforms, scales, /*numIterations=*/3, /*autoMode=*/true);

// 第二阶段：非刚性拟合（PCA 模型变形）
ActorCreator.FitNonRigid(vertexPositions, transforms, scales, 3, true);

// 第三阶段：逐顶点精细拟合
ActorCreator.FitPerVertex(vertexPositions, transforms, scales, 3);

// 设置拟合参数
ActorCreator.SetLandmarksWeight(0.01f);
ActorCreator.SetMinimumDistanceThreshold(1.0f);
ActorCreator.SetModelRegularization(100.0f);
```

### 基本用法 - MetaHuman Creator（面部编辑）

程序化编辑面部形状（来源：`Private/api/MetaHumanCreatorAPI.h`）：

```cpp
#include "api/MetaHumanCreatorAPI.h"

// 从 DNA 创建 API 实例
dna::Reader* dnaReader = /* 加载 DNA 文件 */;
auto MhcApi = TITAN_API_NAMESPACE::MetaHumanCreatorAPI::CreateMHCApi(
    dnaReader, "path/to/mhc_data");

// 创建编辑状态
auto State = MhcApi->CreateState();

// 获取预设列表
std::vector<std::string> presets = MhcApi->GetPresetNames();
std::vector<std::string> regions = MhcApi->GetRegionNames();

// 获取表达式名称
std::vector<std::string> expressions = MhcApi->GetExpressionNames();

// 评估当前状态获取顶点
int numVertices = MhcApi->NumVertices();
std::vector<float> vertices(numVertices * 3);
MhcApi->Evaluate(*State, vertices.data());

// 获取网格顶点（按 DNA Mesh 索引）
Eigen::Matrix<float, 3, -1> meshVertices;
MhcApi->GetMeshVertices(vertices.data(), 0, meshVertices); // mesh 0 = face

// 获取绑定姿态（关节位置）
Eigen::Matrix<float, 3, -1> bindPose;
MhcApi->GetBindPose(vertices.data(), bindPose);

// 编辑 Gizmo（区域变形手柄）
int gizmoIndex = 0;
float delta[3] = {0.1f, 0.0f, 0.0f};
State->TranslateGizmo(gizmoIndex, delta, /*bSymmetric=*/true);

// 设置 Gizmo 旋转
float euler[3] = {5.0f, 0.0f, 0.0f}; // 度
State->SetGizmoRotation(gizmoIndex, euler, /*bSymmetric=*/true);

// 混合到预设
TITAN_API_NAMESPACE::MetaHumanCreatorAPI::State::BlendOptions options;
options.Type = TITAN_API_NAMESPACE::MetaHumanCreatorAPI::State::FaceAttribute::Both;
options.bBlendSymmetrically = true;
State->SelectPreset(gizmoIndex, "preset_name", options);

// 将状态导出为 DNA
dna::Writer* dnaWriter = /* 创建 writer */;
MhcApi->StateToDna(*State, dnaWriter);
```

### 基本用法 - MetaHuman Creator Body（身体编辑）

程序化编辑身体形状（来源：`Private/api/MetaHumanCreatorBodyAPI.h`）：

```cpp
#include "api/MetaHumanCreatorBodyAPI.h"

// 创建 Body API 实例
auto BodyApi = TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::CreateMHCBodyApi(
    pcaBodyDnaReader, combinedArchetypeReader,
    "path/to/rbf_model", "path/to/skin_model",
    "path/to/skinning_weight_config");

// 创建身体编辑状态
auto BodyState = BodyApi->CreateState();

// 获取 GUI 控制名称
std::vector<std::string> guiNames = BodyApi->GetGuiControlNames();
std::vector<std::string> rawNames = BodyApi->GetRawControlNames();

// 获取区域名称
std::vector<std::string> regions = BodyApi->GetRegionNames();

// 评估当前状态
BodyApi->Evaluate(*BodyState);

// 获取网格数据
auto mesh = BodyState->GetMesh(/*lod=*/0);
auto bindPose = BodyState->GetBindPose();

// 混合到预设
TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::BodyAttribute type =
    TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::BodyAttribute::Both;
BodyApi->Blend(*BodyState, /*regionIndex=*/-1, /*states*/{}, type);

// 选择预设身体
BodyApi->SelectPresetBody(*BodyState, /*presetIndex=*/0);

// 拟合到目标网格
TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::FitToTargetOptions fitOptions;
fitOptions.iterations = 9;
BodyApi->FitToTarget(*BodyState, fitOptions, targetVertices);

// 导出为 DNA
BodyApi->StateToDna(*BodyState, dnaWriter);

// 获取测量数据
Eigen::VectorXf measurements;
std::vector<std::string> measurementNames;
BodyApi->GetMeasurements(combinedVertices, measurements, measurementNames);
```

### 基本用法 - Evaluate Rig（Rig 评估）

评估 DNA 骨骼控制器（来源：`Private/api/EvaluateRigAPI.h`）：

```cpp
#include "api/EvaluateRigAPI.h"

TITAN_API_NAMESPACE::EvaluateRigAPI RigEvaluator;

// 加载 DNA
dna::Reader* dnaReader = /* 加载 DNA 文件 */;
RigEvaluator.LoadDNA(dnaReader);

// 获取信息
int numMeshes, numLODs;
RigEvaluator.GetNumMeshes(numMeshes);
RigEvaluator.GetNumLODs(numLODs);

std::vector<std::string> meshNames;
RigEvaluator.GetMeshNames(meshNames);

std::vector<std::string> controlNames;
RigEvaluator.GetRawControlNames(controlNames);

// 设置控制器值并评估
std::map<std::string, float> controls;
controls["CTRL_expressions.Brow_Raise_L"] = 0.5f;
controls["CTRL_expressions.Smile_L"] = 0.8f;

std::vector<int> meshIndices = {0, 1}; // face, teeth
int lod = 0;
std::vector<Eigen::Matrix<float, 3, -1>> meshVertices;
RigEvaluator.EvaluateRawControls(controls, meshIndices, lod, meshVertices);
```

### 进阶用法 - Actor Refinement（Rig 精修）

精修骨骼以匹配编辑后的网格（来源：`Private/api/ActorRefinementAPI.h`）：

```cpp
#include "api/ActorRefinementAPI.h"

TITAN_API_NAMESPACE::ActorRefinementAPI Refiner;

// 更新牙齿模型和位置
dna::Writer* outDna = /* 创建 writer */;
Refiner.UpdateRigWithTeethMeshVertices(dnaReader, teethVertexPositions, outDna);

// 更新头部网格（包含头、牙齿、左右眼）
Refiner.UpdateRigWithHeadMeshVertices(
    dnaReader, headVertices, teethVertices,
    leftEyeVertices, rightEyeVertices, outDna);

// 精修 Rig（体素变形）
std::map<std::string, const float*> targetVertices;
std::map<std::string, std::tuple<std::string, std::vector<int>, std::vector<std::vector<float>>>> deltaData;
Refiner.RefineRig(dnaReader, targetVertices, outDna, deltaData);

// 牙齿放置优化
Refiner.RefineTeethPlacement(dnaReader, refDnaReader, controlsConfigJson, outDna);

// 变换 Rig 原点
float transformMatrix[16]; // 4x4 column-major
Refiner.TransformRigOrigin(dnaReader, transformMatrix, outDna);

// 缩放 Rig
Refiner.ScaleRig(dnaReader, 1.5f, scalingPivot, outDna);

// 应用 Delta DNA
dna::Writer* finalDna = /* 创建 writer */;
Refiner.ApplyDNA(dnaReader, deltaDnaReader, finalDna);

// 生成 Delta DNA
Refiner.GenerateDeltaDNA(fromDna, toDna, deltaDna);
```

### 进阶用法 - Rig Morph（体素变形）

将网格变化传递到骨骼（来源：`Private/rigmorpher/include/rigmorpher/RigMorphModule.h`）：

```cpp
#include "rigmorpher/RigMorphModule.h"

// 体素变形：将目标网格形状变化传递到 DNA
std::map<std::string, Eigen::Matrix<float, 3, -1>> targetVertices;
targetVertices["face"] = editedFaceVertices;

std::vector<std::string> drivingMeshNames = {"face"};
std::vector<std::string> inactiveJointNames = {};
std::map<std::string, std::vector<std::string>> drivenJointNames;
std::map<std::string, std::vector<std::string>> deltaTransferMeshNames;
std::map<std::string, std::vector<std::string>> rigidTransformMeshNames;
std::map<std::string, std::vector<std::string>> uvProjectionMeshNames;

TITAN_NAMESPACE::RigMorphModule<float>::Morph(
    dnaReader, dnaWriter, targetVertices,
    drivingMeshNames, inactiveJointNames,
    drivenJointNames, {}, {}, /*jointsToOptimize*/{},
    deltaTransferMeshNames, rigidTransformMeshNames,
    uvProjectionMeshNames, mainMeshGridDeformMask,
    /*gridSize=*/128, /*inParallel=*/true);
```

## Demo 示例

一个最小示例，演示如何加载 DNA 并评估 Rig 控制器：

```cpp
// MyMetaHumanEvaluator.h
#pragma once

#include "CoreMinimal.h"

class FMyMetaHumanEvaluator
{
public:
    /** 从 DNA 文件路径加载并评估 */
    static bool EvaluateExpression(const FString& DNAFilePath,
                                    const TMap<FString, float>& Controls,
                                    int32 LOD);
};

// MyMetaHumanEvaluator.cpp
#include "MyMetaHumanEvaluator.h"
#include "api/EvaluateRigAPI.h"

// 注意：实际使用时需要通过 DNA SDK 的 Reader 加载 DNA 文件
// 此处为概念示例

bool FMyMetaHumanEvaluator::EvaluateExpression(
    const FString& DNAFilePath,
    const TMap<FString, float>& Controls,
    int32 LOD)
{
    // 1. 创建 API 实例
    TITAN_API_NAMESPACE::EvaluateRigAPI RigEvaluator;

    // 2. 加载 DNA（实际需要通过 DNA SDK Reader）
    dna::Reader* DnaReader = nullptr; // 需要通过实际路径加载
    if (!RigEvaluator.LoadDNA(DnaReader))
    {
        return false;
    }

    // 3. 获取网格信息
    int32 NumMeshes = 0;
    RigEvaluator.GetNumMeshes(NumMeshes);

    std::vector<std::string> MeshNames;
    RigEvaluator.GetMeshNames(MeshNames);

    // 4. 构建控制器映射
    std::map<std::string, float> ControlMap;
    for (const auto& [Name, Value] : Controls)
    {
        ControlMap[std::string(TCHAR_TO_UTF8(*Name))] = Value;
    }

    // 5. 评估所有网格
    std::vector<int> MeshIndices(NumMeshes);
    std::iota(MeshIndices.begin(), MeshIndices.end(), 0);

    std::vector<Eigen::Matrix<float, 3, -1>> OutVertices;
    if (!RigEvaluator.EvaluateRawControls(ControlMap, MeshIndices, LOD, OutVertices))
    {
        return false;
    }

    // 6. 输出结果
    for (int i = 0; i < (int)OutVertices.size(); ++i)
    {
        UE_LOG(LogTemp, Log, TEXT("Mesh '%hs': %d vertices"),
               MeshNames[i].c_str(), (int)OutVertices[i].cols());
    }

    return true;
}
```

## 模块依赖

该插件包含 6 个运行时模块，以下是各模块的特殊依赖：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线服务（用于 MetaHuman Creator 云端交互） |
| `UnrealEd` | 编辑器功能（某些模块在编辑器上下文中运行） |
| `OpenCVHelper` | OpenCV 辅助库（面部关键点检测/图像处理） |
| `OpenCV` | 计算机视觉库（图像处理、相机标定） |
| `DirectoryWatcher` | 文件系统监视（监控捕捉数据目录变化） |
| `MetaHumanImageViewer` | 图像查看器（显示捕捉的图像数据） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | Titan 核心库更新至 v9.0.8 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | Titan 核心库更新至 v9.0.7 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | Titan 核心库更新至 v9.0.6 |
| 2026-05-20 | `c5214fb2` | [MetaHumanBodyTracker] allow foot-locking to be toggled on or off | 身体追踪器新增脚部锁定开关功能 |
| 2026-05-19 | `a29cddd9` | [MHA] Crash during MHC assembly with body performance | 修复身体性能模式下 MHC 组装时的崩溃 |

### 维护评价

- **活跃维护** ✅：最近持续有 Titan 核心库版本更新（v9.0.6 → v9.0.8），更新频率约每周数次。
- **持续演进**：从创建时间至今约 4 年，代码库已从早期版本演进到 Titan v9.x，代表了成熟的技术栈。
- **核心组件**：作为 MetaHuman 生态系统的基础层，受到 Epic Games 的重点维护。
- **大规模代码库**：583 个源文件，包含完整的数值优化、几何处理、PCA 模型、网格拟合等基础设施。
- **非独立使用**：此插件不是独立功能插件，而是 MetaHuman Creator 和 MetaHuman Animator 的底层依赖。
- **需要 DNA SDK**：大量 API 依赖 `dna::Reader` / `dna::Writer`，需要 MetaHuman DNA SDK 支持。
- **推荐使用**：如果你在开发与 MetaHuman 相关的自定义管线（如程序化角色创建、批量处理），这是一个强大的底层工具。但日常用户应使用上层的 MetaHuman Creator / Animator 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- 官方文档（无公开链接）