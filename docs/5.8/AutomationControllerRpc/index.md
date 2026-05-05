# Automation Controller RPC Component

> Enabling the use of the Automation Controller to run registered tests through remote procedure calls

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationControllerRpc` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AutomationControllerRpc) | |

## 用途

该插件为 UE5 的自动化测试控制器（Automation Controller）提供了一个基于 HTTP 的远程过程调用（RPC）接口。它允许外部系统（如持续集成服务器、自定义测试管理工具或脚本）通过标准的 HTTP 请求来远程触发、监控和管理引擎内的自动化测试流程，而无需直接操作编辑器或使用命令行参数。这解决了自动化测试与外部系统集成的难题，实现了测试执行的远程化和自动化。

## 使用场景

- 你的 CI/CD 管道（如 Jenkins, GitLab CI）需要在构建完成后自动触发 UE 项目的自动化测试套件。
- 你正在开发一个自定义的测试仪表板或管理工具，需要从外部查询引擎中注册的测试列表、启动测试并获取结果报告。
- 你需要在分布式测试环境中，从一个中心节点协调多个 UE 实例执行测试。

## 蓝图用法

此插件主要通过 HTTP API 提供功能，不直接暴露蓝图节点。其核心功能由 C++ 类 `UAutomationControllerRpcRegistrationComponent` 管理，并在模块启动时自动注册 HTTP 路由。外部系统通过向引擎的 HTTP 服务器发送请求来使用。

### 核心 HTTP 端点

| 端点 | 说明 | 对应 C++ 方法 |
|---|---|---|
| `POST /automation/controller/initialize` | 初始化自动化控制器 | `HttpAutomationControllerInitializeCommand` |
| `GET /automation/controller/state` | 获取控制器当前状态（如空闲、查找Worker、执行中等） | `HttpAutomationControllerGetStateCommand` |
| `GET /automation/controller/availabletests` | 获取所有已注册的自动化测试列表 | `HttpAutomationControllerGetAvailableTestsCommand` |
| `POST /automation/controller/runtests` | 触发执行指定的测试 | `HttpAutomationControllerRunTestsCommand` |
| `POST /automation/controller/generatereports` | 生成上一次测试执行的报告 | `HttpAutomationControllerGenerateReportsCommand` |

### 使用示例（外部调用）

1.  **初始化控制器**：向 `http://<引擎IP>:<端口>/automation/controller/initialize` 发送 POST 请求。
2.  **查询状态**：向 `http://<引擎IP>:<端口>/automation/controller/state` 发送 GET 请求，返回的 JSON 中包含 `EAutomationControllerState` 枚举值。
3.  **获取测试列表**：向 `http://<引擎IP>:<端口>/automation/controller/availabletests` 发送 GET 请求。
4.  **运行测试**：向 `http://<引擎IP>:<端口>/automation/controller/runtests` 发送 POST 请求，请求体中可指定要运行的测试。
5.  **生成报告**：测试完成后，向 `http://<引擎IP>:<端口>/automation/controller/generatereports` 发送 POST 请求。

## C++ 用法

### 头文件引入

```cpp
#include "AutomationControllerRpcRegistrationComponent.h"
```

### 基本用法

获取 RPC 注册组件的单例实例。通常，插件模块会在启动时自动完成注册，但你也可以在需要时主动访问该实例。

```cpp
// 获取 AutomationControllerRpc 注册组件的单例实例
UAutomationControllerRpcRegistrationComponent* RpcComponent = UAutomationControllerRpcRegistrationComponent::GetInstance();
if (RpcComponent)
{
    // 实例已存在，插件已正确加载并初始化
    UE_LOG(LogTemp, Log, TEXT("AutomationControllerRpc 组件已就绪。"));
}
```
*来源：`AutomationControllerRpcRegistrationComponent.h` 中 `GetInstance()` 的声明*

### 进阶用法

该插件的核心逻辑封装在 `FAutomationControllerRpcBridge` 中，并通过 `UAutomationControllerRpcRegistrationComponent` 注册为 HTTP 回调。作为插件使用者，你通常不需要直接操作这些内部类。你的主要交互方式是通过上述的 HTTP API。

如果你需要扩展或修改 RPC 行为，可以继承 `UAutomationControllerRpcRegistrationComponent` 并重写 `RegisterAlwaysOnHttpCallbacks` 方法。

## Demo 示例

以下示例展示了如何在你的游戏模块中检查此插件是否已加载并可用。

**MyGameModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyGameModule.cpp**
```cpp
#include "MyGameModule.h"
#include "AutomationControllerRpcRegistrationComponent.h"

#define LOCTEXT_NAMESPACE "FMyGameModule"

void FMyGameModule::StartupModule()
{
    // 检查 AutomationControllerRpc 插件是否已加载
    UAutomationControllerRpcRegistrationComponent* RpcComponent = UAutomationControllerRpcRegistrationComponent::GetInstance();
    if (RpcComponent)
    {
        UE_LOG(LogTemp, Display, TEXT("AutomationControllerRpc 插件已加载，可通过 HTTP API 进行远程测试控制。"));
        // 在此处可以添加依赖于此插件的初始化逻辑
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("AutomationControllerRpc 插件未加载，远程测试控制功能不可用。"));
    }
}

void FMyGameModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyGameModule, MyGame)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AutomationController` | 提供核心的自动化测试控制器功能，是本插件进行 RPC 封装的基础。 |

## 维护状态

### 近期更新

- 2026-02-26 17d4bbb6 Adding plugin to trigger AutomationController from RPCs

### 维护评价

- **创建时间**：该插件于 2026 年 2 月创建，非常新。
- **更新频率**：目前仅有一次初始提交，表明它是一个刚引入的实验性功能。
- **活跃度**：作为实验性插件，它可能正在积极开发中，但目前功能和 API 可能不稳定。
- **已知限制**：标记为 `IsExperimentalVersion: true`，且默认未启用 (`Installed: false`)，表明 Epic 可能认为其尚未达到生产就绪状态。
- **推荐使用**：**谨慎使用**。适合用于研究、原型开发或非关键的自动化流程。在生产环境或稳定项目中使用前，需评估其稳定性和未来可能发生的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AutomationControllerRpc)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中发现)