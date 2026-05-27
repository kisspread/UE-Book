# Dump GPU Services

> Implements automatic upload services for the DumpGPU command.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | GPU转储上传服务 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DumpGPUServices` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-24 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DumpGPUServices) | |

## 用途

本插件是 UE 内置 `DumpGPU` 命令（常用于调试渲染问题、捕获 GPU 帧数据）的配套服务。其核心功能不是执行转储本身，而是为转储后的数据提供自动化的上传通道。解决了 `DumpGPU` 命令生成的数据（可能非常大）需要手动处理或分享的问题，通过集成此服务，可以将转储结果自动上传至指定的服务器或存储位置，便于团队协作、远程分析和自动化测试流水线。

## 使用场景

- **性能与渲染自动化测试**：在持续集成（CI）流程中，自动化执行场景测试并调用 `DumpGPU`，随后利用本服务将捕获的 GPU 帧数据上传至分析服务器，用于后续的自动回归或性能分析。
- **远程 GPU 问题诊断**：开发者在本地执行 `DumpGPU` 复现问题后，可以自动将数据上传，供远程的图形工程师或支持团队下载分析，无需手动传输大文件。
- **团队共享与资产审查**：将具有特定视觉问题的帧捕获数据自动共享到团队存储库，用于 Bug 跟踪或美术资产效果审查。

## 蓝图用法

基于当前提供的源码分析，`IDumpGPUServices` 接口**未暴露任何蓝图可调用的函数（BlueprintCallable）或属性（BlueprintReadWrite）**。它主要提供的是 C++ 模块接口，用于程序化地访问上传服务。上传的触发很可能与 `DumpGPU` 控制台命令本身绑定，而非通过蓝图节点直接调用。

## C++ 用法

### 头文件引入

```cpp
#include "IDumpGPUServices.h"
```

### 基本用法

该模块的核心使用模式是获取其单例接口，并检查其可用性。这通常用于在尝试调用上传服务前进行安全检查。

（来源：`Source/DumpGPUServices/Public/IDumpGPUServices.h`）

```cpp
// 检查 DumpGPU 上传服务模块是否已加载并可用
if (IDumpGPUServices::IsAvailable())
{
    // 获取模块实例
    IDumpGPUServices& DumpGPUServicesModule = IDumpGPUServices::Get();
    
    // 此时，该模块实例可用于触发或管理上传操作
    // 具体的上传功能可能需要调用此模块提供的其他未在当前接口中暴露的方法
    // （注：由于提供的接口仅为基本模块访问，实际上传函数可能位于模块内部实现中）
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("DumpGPUServices module is not loaded. Upload functionality is unavailable."));
}
```

### 进阶用法

结合 `DumpGPU` 命令使用。你可能会在游戏模块或自定义编辑器工具中，通过控制台命令或程序化方式触发转储，并依赖本服务处理后续上传。

```cpp
// 假设在某个上下文中需要触发GPU转储并上传
if (IDumpGPUServices::IsAvailable())
{
    // 1. 首先，可能通过控制台系统执行DumpGPU命令来捕获数据
    // （请注意，DumpGPU命令本身可能由渲染模块处理，此插件仅负责上传）
    GEngine->Exec(GetWorld(), TEXT("DumpGPU"));
    
    // 2. 上传逻辑很可能在 DumpGPU 命令的实现内部被自动触发，或者通过
    //    IDumpGPUServices 模块暴露的事件/回调来连接。
    //    由于接口未公开具体函数，实际集成需要查阅 DumpGPUServices 模块的完整实现。
    
    UE_LOG(LogTemp, Log, TEXT("GPU dump initiated. Upload service is active and will handle the data."));
}
```

## Demo 示例

以下是一个最小化的示例，展示如何在你的游戏模块中安全地与 `DumpGPUServices` 模块交互。

**MyGameServices.h**
```cpp
#pragma once

class FMyGameServices
{
public:
    /** 检查GPU调试数据上传服务是否可用，并输出状态信息 */
    static void CheckDumpGPUUploadService();
};
```

**MyGameServices.cpp**
```cpp
#include "MyGameServices.h"
#include "IDumpGPUServices.h"

void FMyGameServices::CheckDumpGPUUploadService()
{
    if (IDumpGPUServices::IsAvailable())
    {
        IDumpGPUServices& Service = IDumpGPUServices::Get();
        UE_LOG(LogTemp, Display, TEXT("DumpGPU upload service is loaded and ready."));
        // 此处可以添加调用具体上传服务方法的代码，例如设置上传目标等。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DumpGPU upload service is not available. Ensure the plugin is enabled."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 模块等）。该插件主要提供服务接口，其具体实现可能依赖引擎的渲染模块和网络/存储模块，但作为使用者，通常无需在 `.Build.cs` 中额外添加依赖，除非你需要深度集成或扩展其功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的UE_LOGF格式，跟随引擎日志系统更新。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes. | 移除大量过时的包含顺序兼容性代码，清理技术债务。 |
| 2024-01-19 | `f0294685` | Fixed up a lot of bool-taking container resize functions to take EAllowShrinking instead. | 修复了容器大小调整函数的接口，使用更明确的枚举类型。 |
| 2023-02-21 | `8676f608` | Moving DumpGPU to Public so that DumpGPUServices can访问它 correctly. | 将DumpGPU相关接口公开，确保本服务插件能正确访问。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | （提交信息不完整，疑为批量维护更新） |

### 维护评价

- **年龄**：插件创建于 2022 年 3 月，年龄较轻（约 3 年）。
- **更新频率**：近期（2024-2026年）仍有更新，但均为引擎全局的API清理和适配性提交，**非功能性更新**。最后一次实质性的功能修改可能追溯到创建初期。
- **维护状态**：**维护不活跃**。该插件的功能相对固定和底层，自创建后可能已达到稳定状态，无需频繁更新。但近2年的提交均未涉及新功能或重大修复。
- **已知限制**：源码分析显示，其公开接口非常精简，可能意味着其核心上传逻辑较为封闭，扩展性有限。作为实验性插件，其API和功能在引擎未来版本中可能发生变化。
- **推荐使用**：**有条件推荐**。如果你的项目或工作流**确需**自动化 `DumpGPU` 结果的上传，这是一个官方的解决方案。但需注意它是实验性功能，且接口可能变化。对于简单的手动分析，直接使用 `DumpGPU` 命令并手动处理文件可能更直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DumpGPUServices)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）