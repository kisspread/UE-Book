```markdown
# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可自定义对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

> **注意**：此插件从 `Experimental` 状态迁移而来，当前为 Beta 状态。需手动在项目设置中启用。

## 用途

Mutable 是一套完整的**运行时可自定义对象（Customizable Object）系统**，用于在游戏中创建高度可组合、可参数化的资产。它解决的核心问题是：

- **角色外观自定义**：玩家可以在运行时自由组合不同部位（发型、服装、纹身、伤疤等），系统自动生成最终的网格体、材质和纹理。
- **内存与性能优化**：通过"可变对象"的概念，多个变体共享底层数据，避免为每种组合烘焙独立资产，大幅减少内存占用和磁盘空间。
- **材质合并**：运行时自动将多个纹理层合成为最终材质，减少 draw call。
- **网格体组合**：运行时将多个身体部件合并为单一网格体，支持骨骼蒙皮、物理体、LOD。
- **投影贴花**：支持 3D 投影器（平面、圆柱、包裹），在运行时将图像投影到网格体上。

该插件在编辑器中提供可视化图编辑器（CustomizableObject Editor），通过节点图定义对象的参数化结构；在运行时通过 `FSystem` 和 `FModel` 执行程序化的资产生成。

## 使用场景

- 你在做一个**角色自定义系统**（如 MMO、RPG）→ 用 Mutable 管理发型/服装/纹身等的组合
- 你需要**运行时材质合并**以减少 draw call → 用 Mutable 将多层纹理合并为单张
- 你需要**投影贴花**（枪械刻字、纹身等）→ 用 Mutable 的 Projector 参数
- 你需要**运行时网格体变形**（Reshape/ClipDeform）→ 用 Mutable 的 Mesh 操作
- 你有大量类似的可组合资产需要**内存优化** → 用 Mutable 的增量生成机制

## 蓝图用法

Mutable 的主要蓝图接口在 `CustomizableObject` 模块中，通过 `UCustomizableObjectInstance` 和 `UCustomizableObject` 暴露给蓝图。当前模块文档聚焦于底层 `MutableRuntime`，其核心 API 为 C++ 层面。

### 核心蓝图类（CustomizableObject 模块）

| 类 | 说明 |
|---|---|
| `UCustomizableObject` | 可自定义对象的定义资产（在编辑器中创建） |
| `UCustomizableObjectInstance` | 可自定义对象的运行时实例，持有当前参数值 |
| `UCustomizableObjectSystem` | 单例管理器，控制更新、流送、内存预算 |

## C++ 用法

MutableRuntime 提供了底层的虚拟机执行引擎、图像处理、网格体处理等核心功能。以下示例展示如何与 Mutable 系统交互。

### 头文件引入

```cpp
#include "MuR/System.h"
#include "MuR/Model.h"
#include "MuR/Parameters.h"
#include "MuR/Image.h"
#include "MuR/Mesh.h"
```

### 基本用法 — 参数设置与实例更新

从 `Parameters.h` 和 `System.h` 提取的核心交互流程：

```cpp
#include "MuR/System.h"
#include "MuR/Parameters.h"
#include "MuR/Model.h"

// 假设已有 FModel（编译后的可自定义对象模型）
TSharedPtr<UE::Mutable::Private::FModel> Model = /* ... */;

// 创建运行时实例
UE::Mutable::Private::FSystem System;
TSharedRef<UE::Mutable::Private::FLiveInstance> LiveInstance = System.BeginUpdate(Model, 0 /* State */, 0xFF /* LODMask */);

// 获取参数集并设置参数值
TSharedPtr<const UE::Mutable::Private::FParameters> Parameters = LiveInstance->Parameters;

// 设置布尔参数
Parameters->SetBoolValue(0 /* ParamIndex */, true);

// 设置整数参数
Parameters->SetIntValue(1 /* ParamIndex */, 2 /* Value */);

// 设置浮点参数（0.0 ~ 1.0）
Parameters->SetFloatValue(2 /* ParamIndex */, 0.75f);

// 执行更新 — 系统内部通过虚拟机生成最终资源
System.EndUpdate(LiveInstance);
```

> 来源：`Internal/MuR/Parameters.h`、`Internal/MuR/System.h`

### 进阶用法 — 图像操作

MutableRuntime 包含完整的图像处理管线，支持像素格式转换、mipmap 生成、RLE 压缩等：

```cpp
#include "MuR/Image.h"
#include "MuR/ImageTypes.h"

using namespace UE::Mutable::Private;

// 创建一个 RGBA 8-bit 图像，尺寸 512x512，带 4 级 mipmap
TManagedPtr<FImage> MyImage = MakeManaged<FImage>(512, 512, 4, EImageFormat::RGBA_UByte, EInitializationType::Black);

// 获取 mipmap 0 的数据指针
uint8* BaseMipData = MyImage->GetLODData(0);
int32 MipDataSize = MyImage->GetLODDataSize(0);

// 使用 FImageOperator 进行像素格式转换
FImageOperator ImageOp = FImageOperator::GetDefault(nullptr);

// 将 RGBA 转换为 BC3（块压缩）
TManagedPtr<FImage> CompressedImage = ImageOp.ImagePixelFormat(
    3 /* Quality */, MyImage.Get(), EImageFormat::BC3);

// 生成 mipmap
FMipmapGenerationSettings MipSettings;
MipSettings.FilterType = EMipmapFilterType::SimpleAverage;
ImageOp.ImageMipmap(3 /* Quality */, MyImage.Get(), MyImage.Get(), 0, 4, MipSettings);

// 检测纯色图像
FVector4f PlainColor;
bool bIsPlain = MyImage->IsPlainColor(PlainColor);
```

> 来源：`Internal/MuR/Image.h`、`Internal/MuR/ImageTypes.h`

### 进阶用法 — RLE 图像压缩

```cpp
#include "MuR/ImageRLE.h"

using namespace UE::Mutable::Private;

// 压缩单通道图像为 RLE
TManagedPtr<FImage> CompressedL = MakeManaged<FImage>(256, 256, 1, EImageFormat::L_UByteRLE, EInitializationType::NotInitialized);
CompressRLE_L(MyLImage.Get(), CompressedL.Get());

// 解压 RLE 图像
TManagedPtr<FImage> Decompressed = MakeManaged<FImage>(256, 256, 1, EImageFormat::L_UByte, EInitializationType::NotInitialized);
UncompressRLE_L(CompressedL.Get(), Decompressed.Get());
```

> 来源：`Private/MuR/ImageRLE.h`

### 进阶用法 — 网格体操作

```cpp
#include "MuR/Mesh.h"
#include "MuR/MeshPrivate.h"

using namespace UE::Mutable::Private;

// 遍历网格体顶点位置
UntypedMeshBufferIteratorConst PosIter(MyMesh->GetVertexBuffers(), EMeshBufferSemantic::Position, 0);
for (int32 v = 0; v < MyMesh->GetVertexCount(); ++v)
{
    FVector3f Position = PosIter.GetAsVec3f();
    ++PosIter;
}

// 遍历骨骼权重
UntypedMeshBufferIteratorConst BoneIdxIter(MyMesh->GetVertexBuffers(), EMeshBufferSemantic::BoneIndices, 0);
UntypedMeshBufferIteratorConst BoneWtIter(MyMesh->GetVertexBuffers(), EMeshBufferSemantic::BoneWeights, 0);
```

> 来源：`Internal/MuR/MeshPrivate.h`

## Demo 示例

以下是一个最小示例，展示如何创建图像并执行格式转换：

```cpp
// MutableDemo.h
#pragma once

#include "CoreMinimal.h"

class FMutableDemo
{
public:
    static void RunDemo();
};
```

```cpp
// MutableDemo.cpp
#include "MutableDemo.h"
#include "MuR/Image.h"
#include "MuR/ImageTypes.h"

using namespace UE::Mutable::Private;

void FMutableDemo::RunDemo()
{
    // 创建 256x256 的 RGBA 图像，带 1 级 mipmap，初始化为黑色
    TManagedPtr<FImage> SourceImage = MakeManaged<FImage>(256, 256, 1, EImageFormat::RGBA_UByte, EInitializationType::Black);

    // 写入一些像素数据（红色渐变）
    uint8* Data = SourceImage->GetLODData(0);
    for (int32 y = 0; y < 256; ++y)
    {
        for (int32 x = 0; x < 256; ++x)
        {
            int32 Offset = (y * 256 + x) * 4;
            Data[Offset + 0] = static_cast<uint8>(x);       // R
            Data[Offset + 1] = 0;                            // G
            Data[Offset + 2] = 0;                            // B
            Data[Offset + 3] = 255;                          // A
        }
    }

    // 创建图像操作器并转换为灰度格式
    FImageOperator ImageOp = FImageOperator::GetDefault(nullptr);
    TManagedPtr<FImage> GrayImage = ImageOp.ImagePixelFormat(1, SourceImage.Get(), EImageFormat::L_UByte);

    // 验证
    if (GrayImage)
    {
        int32 GrayDataSize = GrayImage->GetLODDataSize(0);
        // GrayDataSize 应为 256 * 256 * 1 = 65536
    }

    // 克隆图像
    TManagedPtr<FImage> ClonedImage = SourceImage->Clone();

    // 检查是否纯色
    FVector4f PlainColor;
    bool bIsPlain = SourceImage->IsPlainColor(PlainColor);
    // bIsPlain == false（因为是渐变色）
}
```

## 模块依赖

### MutableRuntime 内部依赖

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | 运行时数据缓存 |
| `MutableTools` | 编译期工具（仅 CustomizableObject 模块依赖） |

### 使用者的依赖

要使用 Mutable 的可自定义对象功能，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | 底层运行时引擎（图像/网格体/虚拟机） |
| `CustomizableObject` | UE 可自定义对象资产类型与实例管理 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名骨骼网格体导致的几何体重复问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作未加载正确 mipmap 的问题 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数计算 LODBias 方法错误的问题 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过 ClothingAssetBase 接口支持更多服装资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能出现的数据竞争 |

### 维护评价

- **状态**：**活跃维护中**。作为 Epic 官方的可自定义对象系统，持续获得功能性更新和 Bug 修复。
- **年龄**：约 1 年（2024 年 9 月从 Experimental 升级为 Beta），但底层技术（原名 Mutable）有更长历史。
- **更新频率**：非常活跃，仅 2026-05-25 ~ 05-26 就有 5 次提交，涵盖骨骼网格体、纹理、布料等多个子系统。
- **已知限制**：当前仍为 Beta 状态（`IsBetaVersion=true`），`EnabledByDefault=false` 需手动启用。
- **源码规模**：1206 个源文件，属于超大型插件，包含完整的编译器、虚拟机、图像/网格体处理器和运行时压缩库（MIRO）。
- **推荐**：✅ **推荐使用**。这是 Epic 官方维护的角色自定义系统，API 稳定，功能完善，适合需要运行时角色/资产可自定义的项目。注意 Beta 状态可能带来 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjects/)
```