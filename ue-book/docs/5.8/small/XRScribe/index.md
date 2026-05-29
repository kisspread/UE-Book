# XRScribe

> OpenXR API Capture/Emulation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | XR记录回放 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRScribe` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-04-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XR/XRScribe) | |

## 用途

XRScribe 是一个用于记录和回放 OpenXR API 调用的工具插件。它解决了在没有真实 XR 硬件（如 VR 头显或手柄）时，对 XR 应用进行开发、调试和自动化测试的问题。

其核心工作原理是：
1.  **记录（Capture）**：在运行时作为 OpenXR API 层，拦截应用对 OpenXR 运行时的所有调用（如创建实例、定位空间、同步动作等），并将这些调用及其参数序列化保存到 `.xrs` 文件中。
2.  **回放（Emulate）**：在没有 XR 硬件的环境下，读取之前保存的 `.xrs` 文件，并模拟一个 OpenXR 运行时。它根据记录的调用历史，为应用生成模拟的会话、空间定位和输入动作状态，使得应用逻辑可以像在真实设备上一样运行。

通过这种方式，开发者可以脱离物理设备，进行大部分基于 OpenXR API 的逻辑测试和功能验证。

## 使用场景

- 你正在开发一个 VR 游戏，但在办公室没有 VR 设备时，想测试手柄交互逻辑是否正确 → 使用 XRScribe 的 **记录模式**，在有设备时记录一次完整操作，之后可在无设备时通过 **回放模式** 反复调试。
- 你需要为 XR 应用编写自动化测试用例，验证用户输入导致的游戏状态变化 → 使用 XRScribe 的 **回放模式**，回放预先录制的输入序列，并断言游戏状态。
- 你想分析一个 XR 应用在特定交互场景下的 OpenXR API 调用时序和参数 → 使用 XRScribe 的 **记录模式** 导出调用日志文件。
- 你正在为多人 XR 应用开发同步逻辑，需要模拟不同客户端的视角和输入 → 可以为每个客户端录制不同的 `.xrs` 文件，在开发机上分别回放。

## 蓝图用法

XRScribe 主要通过引擎开发者设置进行配置，不提供可直接在蓝图中调用的通用业务节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RunMode` | 控制 XRScribe 的运行模式：0-记录，1-回放。 | `UXRScribeDeveloperSettings` |

### 使用示例（蓝图描述）

1.  打开 **项目设置** > **引擎** > **XRScribe**。
2.  在 **Run Mode** 下拉菜单中选择 `Emulate` 以启用回放模式。
3.  重新启动编辑器（此设置需要重启生效）。
4.  运行你的 XR 项目。XRScribe 将尝试从项目目录下的 `Saved/Capture.xrs` 文件加载数据并模拟运行。
5.  若选择 `Capture` 模式运行，应用关闭后，捕获的数据将自动保存至 `Saved/Capture.xrs`。

## C++ 用法

XRScribe 主要通过其内部 API 层（`IOpenXRAPILayer`）与 OpenXR 运行时交互。对于插件开发者或高级用户，可以通过模块接口间接使用。

### 头文件引入

```cpp
#include "XRScribeModule.h" // 主要的模块入口
#include "XRScribeAPISurface.h" // API 层管理器接口
```

### 基本用法

以下示例展示了如何检查 XRScribe 模块是否加载并获取其接口。

```cpp
// 来源: 基于 XRScribeModule.h 的接口设计
#include "XRScribeModule.h"
#include "Modules/ModuleManager.h"

void CheckXRScribeStatus()
{
    FXRScribeModule* XRScribeModule = FXRScribeModule::Get();
    if (XRScribeModule)
    {
        UE_LOG(LogTemp, Log, TEXT("XRScribe 模块已加载。"));
        // 注意：FXRScribeModule 主要作为 OpenXR 扩展插件注册，其公共接口有限。
        // 主要的交互是通过 OpenXR API 链自动完成的。
    }
    else
    {
        UE_LOG(LogWarning, Log, TEXT("XRScribe 模块未加载。请检查插件是否启用。"));
    }
}

// 来源: XRScribeAPISurface.h - 管理函数映射
void ManageXRScribeFunctionMaps()
{
    // 通常由模块内部调用，但展示其存在。
    UE::XRScribe::BuildFunctionMaps();
    // ... 执行一些操作 ...
    UE::XRScribe::ClearFunctionMaps();
}
```

### 进阶用法

直接与 API 层管理器交互，获取当前活动层（捕获层或模拟层）。这通常由 OpenXR 系统内部调用，但在需要底层干预时可能有用。

```cpp
// 来源: XRScribeAPISurface.h - IOpenXRAPILayerManager 接口
#include "XRScribeAPISurface.h"

void QueryActiveXRScribeLayer()
{
    UE::XRScribe::IOpenXRAPILayerManager& LayerManager = UE::XRScribe::IOpenXRAPILayerManager::Get();
    UE::XRScribe::IOpenXRAPILayer* ActiveLayer = LayerManager.GetActiveLayer();

    if (ActiveLayer)
    {
        // 活动层可以是 FOpenXRCaptureLayer 或 FOpenXREmulationLayer
        // 但它们实现相同的 IOpenXRAPILayer 接口
        // 例如，检查它是否支持某个扩展：
        bool bSupportsVisibilityMask = ActiveLayer->SupportsInstanceExtension("XR_KHR_visibility_mask");
        UE_LOG(LogTemp, Log, TEXT("活动 XRScribe 层支持 Visibility Mask 扩展: %s"), bSupportsVisibilityMask ? TEXT("是") : TEXT("否"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("没有活动的 XRScribe API 层。"));
    }
}
```

## Demo 示例

以下示例展示了如何在模块中初始化和使用 XRScribe 的一部分功能（虽然实际使用中，大部分初始化由 OpenXR 插件和引擎自动处理）。这是一个概念性示例。

```cpp
// XRScribeDemo.h
#pragma once
#include "CoreMinimal.h"

class FXRScribeDemo
{
public:
    static void RunDemo();
};
```

```cpp
// XRScribeDemo.cpp
#include "XRScribeDemo.h"
#include "XRScribeModule.h"
#include "XRScribeAPISurface.h"
#include "XRScribeDeveloperSettings.h"
#include "UObject/Class.h"
#include "Engine/Engine.h"

void FXRScribeDemo::RunDemo()
{
    // 1. 检查模块是否可用
    FXRScribeModule* Module = FXRScribeModule::Get();
    if (!Module)
    {
        UE_LOG(LogTemp, Error, TEXT("XRScribe 模块不可用。"));
        return;
    }

    // 2. 读取开发者设置
    const UXRScribeDeveloperSettings* Settings = GetDefault<UXRScribeDeveloperSettings>();
    if (Settings)
    {
        switch (Settings->RunMode)
        {
        case EXRScribeRunMode::Capture:
            UE_LOG(LogTemp, Log, TEXT("XRScribe 配置为捕获模式。"));
            break;
        case EXRScribeRunMode::Emulate:
            UE_LOG(LogTemp, Log, TEXT("XRScribe 配置为回放模式。"));
            break;
        }
    }

    // 3. 获取 API 层管理器并查询状态
    UE::XRScribe::IOpenXRAPILayerManager& Manager = UE::XRScribe::IOpenXRAPILayerManager::Get();
    Manager.SetFallbackRunMode(Settings ? static_cast<int32>(Settings->RunMode) : 0);

    UE::XRScribe::IOpenXRAPILayer* Layer = Manager.GetActiveLayer();
    if (Layer)
    {
        UE_LOG(LogTemp, Log, TEXT("XRScribe API 层已就绪。"));
        // 在实际运行中，层函数会被 OpenXR 运行时调用链调用。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("XRScribe API 层未激活。这可能是因为 OpenXR 插件未启用或未正确初始化。"));
    }
}
```

## 模块依赖

XRScribe 作为 OpenXR 的 API 层，主要依赖 OpenXR 插件及其定义的类型和接口。无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间更具可移植性。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了 32 位格式说明符在参数为 64 位时应使用 64 位的问题，反之亦然。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏。 |
| 2025-10-30 | `09e49c84` | Replace use of RHIGetNativeDevice with the various RHIGetDevice functions on platform RHI interfaces | 使用平台 RHI 接口上的各种 RHIGetDevice 函数替换 RHIGetNativeDevice 的用法。 |
| 2025-09-26 | `cebe17e9` | Removing more implicit RHICommandList usages by passing command lists around more. In some cases, we | 通过更多地传递命令列表，移除了更多隐式 RHICommandList 用法。 |

### 维护评价

XRScribe 自创建以来（约 2 年），虽然提交频率不算非常高，但最近一年内仍有持续的维护和改进更新，主要集中在编译器兼容性、格式安全和底层 RHI 接口的适配上。这表明该插件仍在维护中，但因其 **实验性** 状态和 **默认不启用** 的特点，它更接近于 Epic 内部或高级开发者的专用工具，而非面向所有开发者的成熟功能。

目前没有发现明确的废弃标记，但由于其技术前沿性和依赖 OpenXR 的特定实现，可能存在未公开的限制或与最新 OpenXR 运行时版本的兼容性问题。**推荐用于开发和测试阶段**，但不建议将其作为最终产品中 XR 功能的核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XR/XRScribe)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XR/XRScribe/Source/XRScribe/Tests) (路径基于惯例推断)