# USDPregen

> Library to assist with pre-generating USD-based content.

| 属性 | 值 |
|---|---|
| 中文名 | USD 预生成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `USDPregenCore` (Runtime), `USDPregenHttpWorker` (Runtime), `USDPregenInterchange` (Runtime), `USDPregenInterchangeEditor` (Runtime), `USDPregenPy` (Runtime), `USDPregenUObjectStorage` (Runtime), `USDPregenWrapper` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen) | |

## 用途

USDPregen 插件并非用于运行时在引擎中直接使用 USD 资产，而是作为一个工具库，旨在帮助用户在编辑器或 CI/CD 环境中，**预先、批量地处理和生成基于 USD (Universal Scene Description) 的内容**。它通过模块化的设计，集成了 HTTP 工作线程、与 Unreal 的 Interchange 框架对接、Python 脚本支持以及 UObject 存储等功能，构建了一个自动化的 USD 资产预处理和生成管线。

## 使用场景

- **影视或建筑可视化项目**：需要将大量 USD 资产（如角色、环境、材质）预先转换、优化或生成为 UE 可直接使用的格式，以加速后续的编辑和构建过程。
- **大型团队协作**：通过脚本（如 Python）控制 USD 资产的预生成过程，确保团队成员获得统一、规范化的资产版本。
- **CI/CD 管道集成**：在持续集成和部署流程中，自动执行 USD 资产的预生成和验证，将 USD 工作流无缝集成到自动化生产线中。
- **自定义 USD 处理逻辑**：当标准 USD 导入流程无法满足特定需求时，可以利用此插件提供的框架开发自定义的预生成逻辑。

## 蓝图用法

由于 USDPregen 主要是一个底层的预生成工具库，其核心功能更偏向于 C++ 和 Python 脚本控制。当前 `USDPregenInterchangeEditor` 模块的公共接口主要为模块生命周期管理，不直接暴露复杂的蓝图节点。主要的预生成功能可能通过 Python 脚本或 C++ 扩展点调用。

### 核心节点
（暂无直接暴露的核心蓝图节点，核心功能通过脚本和底层 API 访问。）

### 使用示例（蓝图描述）
蓝图中通常不直接操作 USD 预生成流程，但可以通过调用蓝图函数来触发基于此插件构建的 Python 脚本或 C++ 子系统，从而间接控制预生成任务。

## C++ 用法

USDPregen 提供了模块化的 C++ API。由于是预生成工具，其用法通常涉及初始化预生成上下文、定义预生成任务、并执行这些任务。

### 头文件引入

具体使用哪个模块取决于功能需求。例如，要使用核心预生成逻辑，可能需要引入：
```cpp
#include "USDPregenCoreModule.h"
```

要与 Interchange 框架交互，可能需要：
```cpp
#include "USDPregenInterchangeModule.h"
```

### 基本用法

基本的预生成流程可能遵循以下模式（基于模块功能推断）：
```cpp
// 伪代码示例，展示可能的使用模式
// 1. 创建或获取一个预生成任务配置
FUSDPregenTaskConfig TaskConfig;
TaskConfig.InputPath = TEXT("/Game/USD/Assets/Character.usd");
TaskConfig.OutputPath = TEXT("/Game/Pregenerated/Character");

// 2. 执行预生成任务（通过特定模块的API）
IUSDPregenCoreModule& PregenCoreModule = FModuleManager::Get().LoadModuleChecked<IUSDPregenCoreModule>(TEXT("USDPregenCore"));
PregenCoreModule.ExecutePregenTask(TaskConfig);
```

*注：以上为基于模块功能的推演示例。实际 API 请参考插件源码中的测试用例或示例项目。*

### 进阶用法

进阶用法可能结合多个模块，例如：
1.  使用 `USDPregenPy` 模块通过 Python 脚本定义复杂的预生成规则和后处理步骤。
2.  使用 `USDPregenHttpWorker` 模块从远程服务器获取 USD 文件进行预处理。
3.  使用 `USDPregenInterchange` 模块将预生成的 USD 资产通过 Interchange 管线安全、高效地导入为 UE 资产。

## Demo 示例

一个最小化的使用示例，展示如何在项目中集成 USDPregenCore 模块来执行一个简单的预生成任务。

**MyPregenUser.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "USDPregenCoreTypes.h" // 假设包含预生成任务类型定义

class FMyPregenUser
{
public:
    void RunSimplePregen();
};
```

**MyPregenUser.cpp**
```cpp
#include "MyPregenUser.h"
#include "Modules/ModuleManager.h"
#include "USDPregenCoreModule.h"

void FMyPregenUser::RunSimplePregen()
{
    // 确保USDPregenCore模块已加载
    IUSDPregenCoreModule* PregenCoreModule = FModuleManager::Get().LoadModulePtr<IUSDPregenCoreModule>(TEXT("USDPregenCore"));
    if (PregenCoreModule)
    {
        // 创建一个简单的预生成任务
        FUSDPregenTask Task;
        Task.InputUSDPath = FSoftObjectPath(TEXT("/Game/USD/InputCube.usd"));
        Task.OutputDirectory = TEXT("/Game/Generated/Cubes");

        // 提交任务
        PregenCoreModule->EnqueuePregenTask(Task);
        UE_LOG(LogTemp, Log, TEXT("USD Pregen task submitted for Cube.usd"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load USDPregenCore module."));
    }
}
```

## 模块依赖

本插件由多个内部模块组成，形成了一个预生成工具栈。

| 模块 | 用途 |
|---|---|
| `UsdPregenCore` | 预生成的核心逻辑和任务调度。 |
| `USDPregenHttpWorker` | 处理通过 HTTP 下载 USD 文件或相关资源的工作线程。 |
| `USDPregenInterchange` | 将预生成结果与 Unreal 的 Interchange 导入/导出框架对接。 |
| `USDPregenInterchangeEditor` | 提供在编辑器环境下与 Interchange 交互的特定功能。 |
| `USDPregenPy` | 提供 Python 脚本接口，用于控制和定制预生成流程。**依赖 Python3 模块。** |
| `USDPregenUObjectStorage` | 管理预生成过程中产生的 UObject 的存储和序列化。 |
| `USDPregenWrapper` | 可能是对底层 USD 库或核心功能的封装层。 |

## 维护状态

### 近期更新
- `9e86e007` 2026-05-14 — [USD] UsdPregen: Fixes regression introduced by recent clean up, where an item can get incorrectly p...
  *修复了近期清理工作引入的回归问题，某物品可能被错误处理。*
- `ddc18470` 2026-05-14 — [USD] UsdPregen: On definition conflicts during registry population, return the existing definition.
  *在注册表填充期间遇到定义冲突时，返回已有的定义。*
- `60206a86` 2026-05-14 — USD Pregen: Batch renaming for consistency. Also changes the default storage plugin in UE to the UOb...
  *批量重命名以保持一致性。同时将 UE 中的默认存储插件更改为 UObject...*
- `bad2257d` 2026-05-14 — USD Pregen: User-configurable template string with placeholders for determining asset path;
  *用户可配置的模板字符串，包含占位符，用于确定资产路径。*
- `9f286b30` 2026-05-14 — USD Pregen: Fix _VT and _NonVT textures not being saved from worker imports.
  *修复工作线程导入时 _VT 和 _NonVT 纹理未被保存的问题。*

### 维护评价
USDPregen 是一个非常新的插件（创建于 2026-05-14），目前处于 **实验性 (Experimental) 和 Beta 阶段**。从最近的 git 历史（5 次提交均在同一天）来看，它正处于 **活跃的早期开发阶段**，频繁进行功能调整、重构和 bug 修复。

- **优势**：开发活跃，Epic Games 正在积极构建和优化。
- **风险**：作为实验性插件，API 和功能可能发生重大变化，稳定性未经充分验证，不建议用于生产项目。
- **推荐**：仅推荐给希望探索 USD 工作流自动化、参与 UE5 前沿功能测试或为未来做技术储备的开发者使用。在正式项目中使用需非常谨慎，并做好应对 breaking changes 的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen/Tests)（如果存在）