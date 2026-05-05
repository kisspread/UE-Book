# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个**运行时可定制对象（Customizable Object）系统**，用于在游戏运行时根据参数动态生成网格体、纹理、材质和骨骼数据。

核心思路：在编辑器中用节点图（类似材质编辑器）定义一个可定制对象的**生成模型（FModel）**，该模型包含所有可能的变体组合逻辑。运行时通过设置**参数（FParameters）**——布尔值、整数、浮点数、颜色、投影器、外部图片/网格体等——来**构建实例（FInstance）**，实例中包含最终可用的 LOD 网格体、纹理、材质引用和骨骼数据。

典型应用场景：角色换装系统。你定义一个角色模型，包含发型、服装、纹身等参数，运行时玩家选择不同组合，Mutable 实时生成对应的最终网格体和纹理，支持 LOD、UV 布局、纹理投影、网格体裁剪/合并等复杂操作。

与传统"预制所有变体"的方式相比，Mutable 的优势在于：
- **内存高效**：不需要预烘焙所有组合，运行时按需生成
- **流式加载**：支持外部数据流式加载（`FModelReader`），降低内存峰值
- **并行执行**：内置并行化支持（`ParallelExecutionUtils`），可利用多核 CPU
- **纹理压缩**：内置 BC1-BC7 和 ASTC 运行时压缩库（Miro），支持多种质量级别

## 使用场景

- 你在做一个 RPG/射击游戏，需要**角色换装系统**（发型、服装、装备、纹身组合）→ 用 Mutable
- 你需要**运行时动态生成纹理**（如投影贴花、程序化纹理混合）→ 用 Mutable 的图像投影系统
- 你需要**运行时合并/裁剪网格体**（如根据装备组合生成最终角色网格体）→ 用 Mutable 的网格体操作
- 你需要**大量变体但不想预烘焙所有组合**（如车辆涂装、武器皮肤）→ 用 Mutable
- 你需要**流式加载大型可定制对象**以控制内存 → 用 Mutable 的外部数据流式系统

## 蓝图用法

> **注意**：MutableRuntime 模块的 API 全部位于 `UE::Mutable::Private` 命名空间，属于底层运行时引擎。蓝图可调用的公开 API 位于 `CustomizableObject` 模块中（如 `UCustomizableObjectInstance`、`UCustomizableObject` 等 UCLASS）。本节仅覆盖 MutableRuntime 模块提供的底层能力。

MutableRuntime 本身不直接暴露蓝图节点。蓝图交互通过 `CustomizableObject` 模块的 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类完成。

### 核心运行时类

| 类 | 说明 | 所在模块 |
|---|---|---|
| `FSystem` | 主系统类，加载模型并构建实例 | `MutableRuntime` |
| `FModel` | 可定制对象模型，包含参数定义和生成逻辑 | `MutableRuntime` |
| `FInstance` | 从模型+参数构建出的实例，包含最终网格体/纹理/材质 | `MutableRuntime` |
| `FParameters` | 模型参数值集合 | `MutableRuntime` |
| `FSettings` | 系统配置（内存限制、压缩质量、性能分析） | `MutableRuntime` |
| `FImage` | 2D 图像资源，支持 mipmap 和多种压缩格式 | `MutableRuntime` |
| `FSkeleton` | 骨骼数据 | `MutableRuntime` |
| `FMaterial` | 材质资源，包含纹理/颜色/标量参数映射 | `MutableRuntime` |
| `FLayout` | UV 布局，定义纹理图块分配策略 | `MutableRuntime` |
| `FExtensionData` | 扩展数据，支持 Mutable 原生不支持的数据类型 | `MutableRuntime` |

## C++ 用法

### 头文件引入

```cpp
#include "MuR/System.h"
#include "MuR/Model.h"
#include "MuR/Parameters.h"
#include "MuR/Instance.h"
#include "MuR/Image.h"
#include "MuR/Mesh.h"
#include "MuR/Settings.h"
```

### 基本用法：创建系统并构建实例

```cpp
// 来源: Engine/Plugins/Mutable/Source/MutableRuntime/Internal/MuR/System.h
// 来源: Engine/Plugins/Mutable/Source/MutableRuntime/Internal/MuR/Settings.h

using namespace UE::Mutable::Private;

// 1. 配置系统设置
FSettings Settings;
Settings.SetWorkingMemoryBytes(256 * 1024 * 1024);  // 限制工作内存为 256MB
Settings.SetImageCompressionQuality(1);               // 最佳运行时质量
Settings.SetProfile(true);                            // 启用性能分析

// 2. 创建系统实例
TSharedPtr<FSystem> System = MakeShared<FSystem>(Settings);

// 3. 加载模型（通常从序列化数据反序列化）
TSharedPtr<FModel> Model;
{
    FInputMemoryStream Stream(Buffer, BufferSize);
    FInputArchive Archive(Stream);
    Model = FModel::StaticUnserialise(Archive);
}

// 4. 创建参数并设置值
TSharedPtr<FParameters> Params = FModel::NewParameters(Model);
Params->SetBoolValue(ParamIndex, true);
Params->SetIntValue(ParamIndex, 2);
Params->SetFloatValue(ParamIndex, 0.75f);

// 5. 构建实例
TSharedPtr<FInstance> Instance = System->BeginUpdate(Model.Get(), Params.Get(), FSystem::AllLODs);
// ... 处理实例数据 ...
System->EndUpdate(Instance.Get());
```

### 进阶用法：图像投影与网格体操作

```cpp
// 来源: Engine/Plugins/Mutable/Source/MutableRuntime/Internal/MuR/OpImageProject.h
// 来源: Engine/Plugins/Mutable/Source/MutableRuntime/Internal/MuR/OpMeshPrepareLayout.h

using namespace UE::Mutable::Private;

// 将纹理投影到网格体上（平面投影）
FScratchImageProject Scratch;
ImageRasterProjectedPlanar(
    Mesh,           // 目标网格体
    TargetImage,    // 输出图像
    SourceImage,    // 投影源图像
    MaskImage,      // 遮罩
    true,           // 启用 RGB 淡出
    true,           // 启用 Alpha 淡出
    ESamplingMethod::Bilinear,
    FadeStart, FadeEnd,
    MipInterpolationFactor,
    LayoutIndex, BlockId,
    CropMin, UncroppedSize,
    &Scratch
);

// 将网格体应用到布局（UV 图块分配）
MeshPrepareLayout(
    *Mesh,
    *Layout,
    LayoutChannel,
    true,   // 归一化 UV
    true,   // 钳制 UV 岛
    true,   // 确保所有顶点都有布局块
    false   // 不使用绝对块 ID
);

// 优化网格体缓冲区以减少内存
MeshOptimizeBuffers(Mesh);
```

### 进阶用法：内存跟踪与并行执行

```cpp
// 来源: Engine/Plugins/Mutable/Source/MutableRuntime/Internal/MuR/MemoryTrackingUtils.h
// 来源: Engine/Plugins/Mutable/Source/MutableRuntime/Internal/MuR/ParallelExecutionUtils.h

using namespace UE::Mutable::Private;

// 查询内存使用峰值
SSIZE_T PeakMemory = FGlobalMemoryCounter::GetPeak();
SSIZE_T CurrentMemory = FGlobalMemoryCounter::GetCounter();

// 重置内存计数器（用于测量特定操作的内存消耗）
FGlobalMemoryCounter::Zero();
// ... 执行操作 ...
SSIZE_T OperationMemory = FGlobalMemoryCounter::GetCounter();
FGlobalMemoryCounter::Restore();

// 并行批量处理（内部使用，用于加速实例构建）
UE::Mutable::Private::ParallelExecutionUtils::InvokeBatchParallelFor(
    NumItems,
    [](int32 Index) {
        // 并行处理每个项目
    }
);
```

## Demo 示例

以下展示如何使用 MutableRuntime 的底层 API 创建一个简单的图像处理流程：

```cpp
// MyMutableExample.h
#pragma once

#include "MuR/System.h"
#include "MuR/Model.h"
#include "MuR/Parameters.h"
#include "MuR/Instance.h"
#include "MuR/Image.h"
#include "MuR/Settings.h"

class FMyMutableExample
{
public:
    /** 初始化 Mutable 系统 */
    void Initialize();
    
    /** 从序列化数据加载模型 */
    bool LoadModel(const uint8* Data, uint64 DataSize);
    
    /** 设置参数并构建实例 */
    TSharedPtr<UE::Mutable::Private::FInstance> BuildInstance(
        int32 HairStyle, 
        float SkinTone, 
        bool bHasHelmet);

private:
    TSharedPtr<UE::Mutable::Private::FSystem> MutableSystem;
    TSharedPtr<UE::Mutable::Private::FModel> MutableModel;
};
```

```cpp
// MyMutableExample.cpp
#include "MyMutableExample.h"

using namespace UE::Mutable::Private;

void FMyMutableExample::Initialize()
{
    FSettings Settings;
    Settings.SetWorkingMemoryBytes(512 * 1024 * 1024); // 512MB 工作内存
    Settings.SetImageCompressionQuality(1);              // 运行时最佳质量
    Settings.SetProfile(false);                          // 关闭性能分析
    
    MutableSystem = MakeShared<FSystem>(Settings);
}

bool FMyMutableExample::LoadModel(const uint8* Data, uint64 DataSize)
{
    FInputMemoryStream Stream(Data, DataSize);
    FInputArchive Archive(Stream);
    MutableModel = FModel::StaticUnserialise(Archive);
    return MutableModel.IsValid();
}

TSharedPtr<FInstance> FMyMutableExample::BuildInstance(
    int32 HairStyle, 
    float SkinTone, 
    bool bHasHelmet)
{
    if (!MutableModel || !MutableSystem)
    {
        return nullptr;
    }

    // 创建默认参数
    TSharedPtr<FParameters> Params = FModel::NewParameters(MutableModel);

    // 查找并设置参数
    int32 HairParamIndex = -1;
    for (int32 i = 0; i < Params->GetCount(); ++i)
    {
        if (Params->GetName(i) == FName("HairStyle"))
        {
            HairParamIndex = i;
            break;
        }
    }
    
    if (HairParamIndex >= 0)
    {
        Params->SetIntValue(HairParamIndex, HairStyle);
    }

    // 构建所有 LOD 的实例
    TSharedPtr<FInstance> Instance = MutableSystem->BeginUpdate(
        MutableModel.Get(), 
        Params.Get(), 
        FSystem::AllLODs
    );
    
    MutableSystem->EndUpdate(Instance.Get());
    
    return Instance;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableTools` | 编辑器工具，用于编译可定制对象图（CustomizableObject 编译依赖） |
| `DerivedDataCache` | 派生数据缓存，用于缓存编译结果 |
| `MessageLog` | 编辑器消息日志，用于显示编译警告和错误 |

> MutableRuntime 模块本身无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

```
- 133c5895b946 [Mutable] Fix crash when generating empty components.
- 5b5965dd5512 [Mutable] Moved missing files MuT and MuR from /Public to /Internal
- 75e4adbd31f8 [Mutable] Change namespace name
```

### 维护评价

- **创建时间**：2022 年 9 月，相对较新的插件（约 3 年）
- **版本号**：1.8.0，表明经历了多次迭代
- **命名空间重构**：近期将代码迁移到 `UE::Mutable::Private` 命名空间，并将文件从 `/Public` 移至 `/Internal`，说明正在进行代码组织优化
- **活跃维护**：最近有实质性 bug 修复（空组件崩溃修复）和代码重构
- **模块数量**：5 个模块，架构清晰（Runtime / Tools / Editor / Validation 分离）
- **源码规模**：1449 个文件，属于大型成熟系统

**推荐使用**：Mutable 是 Epic 官方维护的角色定制系统，被 Fortnite 等大型项目使用。虽然 API 位于 Private 命名空间（表明底层 API 可能变化），但通过 `CustomizableObject` 模块的公开接口使用是稳定的。适合需要运行时角色/装备定制的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjects/)