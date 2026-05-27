# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一套完整的**运行时可定制对象系统**，用于在游戏中实现角色/物品外观的动态定制。它解决的核心问题是：如何让玩家在运行时实时修改游戏对象的网格、材质和纹理，同时保持高性能。

该插件包含三个主要层级：

1. **节点图系统（MutableTools）**：提供一套基于节点（Node）的图结构，艺术家和程序员可以通过组合网格变形、纹理合成、材质切换等节点，定义对象的所有可定制部分。
2. **编译器（Compiler）**：将节点图编译成高度优化的 AST（抽象语法树），再链接成可执行的运行时程序（Program）。编译过程中执行常量折叠、死代码消除、语义优化、LOD 生成等优化。
3. **运行时（MutableRuntime）**：在游戏运行时根据参数动态生成最终的网格和纹理，支持状态切换、增量更新。

简单来说：**Mutable = 节点编辑器定义定制规则 + 编译器优化 + 运行时动态生成**。

## 使用场景

- 你在做一个 RPG/角色扮演游戏，需要让玩家自定义角色外观（发型、肤色、装备组合）→ 用 Mutable
- 你需要一个装备系统，不同装备部件需要动态替换网格和材质 → 用 Mutable
- 你需要大量相似但有差异的 NPC 外观，希望用参数化方式批量生成 → 用 Mutable 的 Table 系统
- 你需要在运行时根据玩家选择动态合成纹理（贴花、图案叠加等）→ 用 Mutable 的图像合成节点
- 你需要根据游戏状态（受伤、变老等）改变角色网格形状 → 用 Mutable 的 MeshMorph/Reshape 系统

## 蓝图用法

MutableTools 模块本身是纯 C++ 编译工具，不直接暴露蓝图节点。蓝图层面的可定制对象 API 位于 `CustomizableObject` 模块中（如 `UCustomizableObject`、`UCustomizableObjectInstance`）。

以下列出 MutableTools 中与运行时交互相关的公共类型（供理解）：

### 核心类型

| 类型 | 说明 |
|---|---|
| `FObjectState` | 描述对象的一个可切换状态（名称、运行时参数列表、优化选项） |
| `CompilerOptions` | 编译器配置（优化开关、压缩质量、纹理布局策略等） |
| `Compiler` | 主编译器入口，将 Node 图编译为运行时 Model |
| `FErrorLog` | 编译错误/警告日志收集器 |

## C++ 用法

MutableTools 是一个内部编译工具模块，其公共 API 主要面向插件内部使用。以下示例展示了编译器的基本使用流程。

### 头文件引入

```cpp
#include "MuT/Compiler.h"
```

### 基本用法：配置编译选项并编译

来源：`Internal/MuT/Compiler.h`

```cpp
// 1. 创建编译器选项
Ptr<UE::Mutable::Private::CompilerOptions> Options = new UE::Mutable::Private::CompilerOptions();
Options->SetOptimisationEnabled(true);          // 启用优化
Options->SetConstReductionEnabled(true);        // 启用常量折叠
Options->SetImageCompressionQuality(100);       // 纹理压缩质量
Options->SetOptimisationMaxIteration(8);        // 最大优化迭代次数
Options->SetEnableProgressiveImages(false);     // 是否生成渐进式图像
Options->SetIgnoreStates(false);                // 是否忽略状态

// 2. 创建编译器
TFunction<void()> WaitCallback = []() { /* 线程同步回调 */ };
UE::Mutable::Private::Compiler Compiler(Options, WaitCallback);

// 3. 编译节点图
TMap<FOperation::ADDRESS, FInstancedStruct> ExternalOperations;
TSharedPtr<FModel> Model = Compiler.Compile(RootNode, ExternalOperations);

// 4. 检查编译日志
TSharedPtr<FErrorLog> Log = Compiler.GetLog();
for (int32 i = 0; i < Log->GetMessageCount(); ++i)
{
    if (Log->GetMessageType(i) == ELMT_ERROR)
    {
        UE_LOG(LogMutable, Error, TEXT("%s"), *Log->GetMessageText(i));
    }
}
```

### 进阶用法：自定义纹理和网格资源回调

来源：`Internal/MuT/Compiler.h`（`FReferencedImageResourceFunc` / `FReferencedMeshResourceFunc`）

```cpp
// 注册外部资源提供回调，用于编译时引用引擎资源（如已有的纹理资产）
auto ImageProvider = [](PASSTHROUGH_ID TextureId,
                        TSharedPtr<TManagedPtr<FImage>> OutImage,
                        bool bRunImmediately) -> UE::Tasks::FTask
{
    // 根据 TextureId 加载对应的引擎纹理并转换为 Mutable 格式
    // ...
    return UE::Tasks::MakeTask(/* ... */);
};

auto MeshProvider = [](PASSTHROUGH_ID MeshId,
                       const FString& MorphName,
                       TSharedPtr<TManagedPtr<FMesh>> OutMesh,
                       bool bRunImmediately) -> UE::Tasks::FTask
{
    // 根据 MeshId 和 MorphName 加载对应的引擎网格
    // ...
    return UE::Tasks::MakeTask(/* ... */);
};

Options->SetReferencedResourceCallback(ImageProvider, MeshProvider);
```

### 进阶用法：自定义纹理像素格式转换

来源：`Internal/MuT/Compiler.h` + `Internal/MuT/UnrealPixelFormatOverride.h`

```cpp
// 使用 Unreal 的纹理压缩管线
PrepareUnrealCompression(); // 必须在 GameThread 调用一次

// 注册自定义像素格式转换函数
Options->SetImagePixelFormatOverride(
    [](bool& bOutSuccess, int32 Quality, FImage* Target, const FImage* Source, int32 OnlyLOD)
    {
        UnrealPixelFormatFunc(bOutSuccess, Quality, Target, Source, OnlyLOD);
    }
);

// 设置纹理布局策略
Options->SetDataPackingStrategy(
    3,          // MinTextureResidentMipCount
    1024 * 64   // EmbeddedDataBytesLimit (字节)
);
```

## Demo 示例

以下展示如何在 C++ 中创建一个简单的编译流程。这是最小可编译示例，假设你已经有了一个构建好的 Node 图。

```cpp
// MutableDemo.h
#pragma once

#include "MuT/Compiler.h"
#include "MuT/Node.h"

class FMutableDemo
{
public:
    /** 编译一个 Mutable 节点图并返回运行时模型 */
    static TSharedPtr<FModel> CompileModel(
        const UE::Mutable::Private::Ptr<UE::Mutable::Private::Node>& RootNode);
};
```

```cpp
// MutableDemo.cpp
#include "MutableDemo.h"
#include "MuT/Compiler.h"
#include "MuT/ErrorLog.h"

TSharedPtr<FModel> FMutableDemo::CompileModel(
    const UE::Mutable::Private::Ptr<UE::Mutable::Private::Node>& RootNode)
{
    using namespace UE::Mutable::Private;

    // 配置编译选项
    Ptr<CompilerOptions> Options = new CompilerOptions();
    Options->SetOptimisationEnabled(true);
    Options->SetConstReductionEnabled(true);
    Options->SetLogEnabled(true);
    Options->SetOptimisationMaxIteration(8);

    // 空的线程同步回调（在编辑器工具管线中通常需要更复杂的实现）
    TFunction<void()> WaitCallback = []() {};

    // 创建编译器并执行编译
    Compiler Compiler(Options, WaitCallback);

    TMap<FOperation::ADDRESS, FInstancedStruct> ExternalOperations;
    TSharedPtr<FModel> Model = Compiler.Compile(RootNode, ExternalOperations);

    // 输出编译日志
    TSharedPtr<FErrorLog> Log = Compiler.GetLog();
    int32 ErrorCount = 0;
    int32 WarningCount = 0;

    for (int32 i = 0; i < Log->GetMessageCount(); ++i)
    {
        switch (Log->GetMessageType(i))
        {
        case ELMT_ERROR:
            UE_LOG(LogTemp, Error, TEXT("[Mutable] %s"), *Log->GetMessageText(i));
            ++ErrorCount;
            break;
        case ELMT_WARNING:
            UE_LOG(LogTemp, Warning, TEXT("[Mutable] %s"), *Log->GetMessageText(i));
            ++WarningCount;
            break;
        case ELMT_INFO:
            UE_LOG(LogTemp, Log, TEXT("[Mutable] %s"), *Log->GetMessageText(i));
            break;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Mutable compilation: %d errors, %d warnings"),
        ErrorCount, WarningCount);

    return Model;
}
```

## 模块依赖

从 `CustomizableObject.Build.cs` 提取的依赖：

| 模块 | 用途 |
|---|---|
| `MutableTools` | Mutable 编译器和节点图工具 |
| `DerivedDataCache` | 编译产物的派生数据缓存 |
| `MessageLog` | 编译错误/警告的消息日志面板 |

> 注：`MutableRuntime`、`MutableTools`、`MutableValidation` 为插件内部模块，`CustomizableObject` 模块依赖 `MutableTools` 进行编译。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名骨骼网格重复几何体的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作未加载正确 mip 级别 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算 LODBias 的错误方法 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过 ClothingAssetBase 接口支持更多服装资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时的潜在数据竞争 |

### 维护评价

Mutable 是一个**活跃维护中**的大型插件：

- **版本成熟度**：版本号已达 1.8.0，虽然 2024 年 9 月才从 Experimental 迁入正式 Plugins 目录，但代码库已有较长历史
- **维护频率**：近期（2026 年 5 月）有密集的 bug 修复更新，表明 Epic 团队正在积极维护
- **代码规模**：1206 个源文件，属于超大型插件，包含完整的编译器、优化器、运行时和编辑器工具
- **Beta 状态**：当前标记为 Beta 版本（从 Experimental 升级），API 可能仍有变动
- **推荐程度**：如果你的项目需要运行时角色/物品定制系统，Mutable 是 UE5 官方提供的唯一完整解决方案，推荐使用但需注意 Beta 状态下 API 可能变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [MutableTools 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Source/MutableTools)
- [MutableRuntime 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Source/MutableRuntime)
- [CustomizableObject 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Source/CustomizableObject)