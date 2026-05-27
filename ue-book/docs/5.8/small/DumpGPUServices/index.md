# Dump GPU Services

> Implements automatic upload services for the DumpGPU command.

| 属性 | 值 |
|---|---|
| 中文名 | GPU转储服务 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DumpGPUServices` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DumpGPUServices) | |

## 用途

DumpGPUServices 插件为 Unreal Engine 的 `DumpGPU` 控制台命令提供了自动上传服务。`DumpGPU` 命令用于捕获当前 GPU 的状态并转储到文件，主要用于图形调试和性能分析。此插件将捕获的数据（如资源、着色器、渲染命令等）自动上传到配置的服务器或存储位置，省去了用户手动处理这些文件的步骤。它通过一个运行时模块（`DumpGPUServices`）实现了这些上传逻辑。

## 使用场景

- 你在进行复杂的图形渲染调试，需要使用 `DumpGPU` 命令频繁捕获 GPU 状态，并希望自动将结果归档或分享给团队。
- 你的开发流程要求将 GPU 调试数据自动集成到持续集成/持续部署 (CI/CD) 系统或内部调试工具中。
- 你需要在多个设备上运行 `DumpGPU`，并希望结果能统一上传到一个中心位置进行分析。

## 蓝图用法

此插件主要提供 C++ 模块接口，并未暴露大量可供蓝图直接调用的函数。其核心功能是扩展 `DumpGPU` 命令的行为，在命令执行的后台自动触发上传服务。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IDumpGPUServices::Get()` | 获取 `DumpGPUServices` 模块的单例引用。 | `IDumpGPUServices` |
| `IDumpGPUServices::IsAvailable()` | 检查 `DumpGPUServices` 模块是否已加载并可用。 | `IDumpGPUServices` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接与此插件交互。它的功能是隐式的：当 `DumpGPU` 命令执行时，插件会自动接管后续的上传流程。你只需在游戏控制台（按 `~` 键）或通过代码执行 `DumpGPU` 命令即可。

如果需要在蓝图中检查插件是否生效，可以使用 “Is Module Loaded” 节点，模块名填写 `DumpGPUServices`。

## C++ 用法

### 头文件引入

```cpp
#include "IDumpGPUServices.h"
```

### 基本用法

此插件主要作为服务存在，其内部逻辑在 `DumpGPU` 命令触发时自动运行。开发者通常通过检查模块的可用性来确认功能就绪。
（来源：`Source/DumpGPUServices/Public/IDumpGPUServices.h`）

```cpp
// 检查 DumpGPUServices 模块是否可用，然后获取其引用
if (IDumpGPUServices::IsAvailable())
{
    IDumpGPUServices& DumpGPUServicesModule = IDumpGPUServices::Get();
    // 可以在此处与模块进行其他交互（如果未来提供了API）
}
```

### 进阶用法

目前插件未公开更多复杂的 API。其主要价值在于后台服务。开发者可以通过子类化或替换模块来扩展上传行为（例如，实现自定义的上传协议），但这需要深入理解其内部实现。

## Demo 示例

由于此插件主要是后台服务，没有独立的最小可运行示例。其效果通过执行 `DumpGPU` 控制台命令来验证。如果配置正确，命令执行后应无报错，且转储文件会被上传。

```cpp
// .h
#pragma once
#include "CoreMinimal.h"
// 无需包含 DumpGPUServices 头文件，除非需要显式检查
```

```cpp
// .cpp
#include "MyClass.h"
#include "IDumpGPUServices.h" // 用于检查可用性

void UMyClass::TestDumpGPU()
{
    // 1. 检查插件模块是否加载
    if (IDumpGPUServices::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("DumpGPU upload service is available. Triggering DumpGPU..."));
        // 2. 通过控制台命令触发 DumpGPU
        GEngine->Exec(nullptr, TEXT("DumpGPU"));
        // 插件将在后台自动处理上传
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DumpGPU upload service module is not loaded."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到新的 UE_LOGF 格式。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 移除了大量在 UE5.2 中被弃用的头文件包含顺序控制宏。 |
| 2024-01-19 | `f0294685` | Fixed up a lot of bool-taking container resize functions to take EAllowShrinking instead. | 修复了多个容器调整大小函数，将布尔参数改为更明确的 EAllowShrinking 枚举。 |
| 2023-02-21 | `8676f608` | Moving DumpGPU to Public so that DumpGPUServices can access it correctly. | 将 DumpGPU 相关内容移动到 Public 目录，以确保 DumpGPUServices 插件能正确访问。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件目录的通用更新或维护。 |

### 维护评价

- **状态**：**维护不活跃**。虽然最近一次更新在 2026 年 4 月，但内容仅为日志宏和代码规范调整（UE_LOGF, Include Order, EAllowShrinking）。这些属于引擎全局的代码现代化工作，并非该插件的功能性更新。
- **最后实质性更新**：2023 年 2 月（`8676f608`）修复了模块间的访问问题，这是最近一次针对插件本身逻辑的修正。
- **活跃度**：插件功能简单且稳定，更新频率低，主要跟随引擎的底层代码重构进行适配。
- **建议**：该插件标记为 `IsExperimentalVersion`，表明其仍处于实验阶段。虽然代码已存在多年，但功能相对单一。如果你的项目严重依赖 `DumpGPU` 的自动化上传，可以启用并使用。但对于核心渲染逻辑没有影响。不推荐在高度稳定或寻找成熟解决方案的生产环境中将其视为关键组件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DumpGPUServices)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DumpGPUServices/Tests) (假设存在)