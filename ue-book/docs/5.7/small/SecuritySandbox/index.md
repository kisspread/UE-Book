# Security Sandbox

> Provides features to help reduce the operating system permissions your game client runs with and therefore reduce the impact to players if an attacker takes control of it through a vulnerability.

| 属性 | 值 |
|---|---|
| 中文名 | 安全沙盒 |
| 分类 | Security |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SecuritySandbox` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 1.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SecuritySandbox) | |

## 用途

本插件提供**运行时权限收缩**能力。游戏进程在启动后可以主动调用 API，将自身操作系统权限降到最低（例如 Windows 上的低完整性级别），从而限制攻击者通过漏洞控制进程后可能造成的破坏（如读写文件、运行子进程、修改系统设置等）。它仅支持 Win64 平台，专为需要高安全性的网络游戏（尤其是有玩家对战、用户生成内容场景）设计。

## 使用场景

- 你的游戏需要加载玩家生成的内容（UGC），担心恶意内容利用文件系统权限进行攻击
- 你的游戏客户端需要联网，但希望即使被攻破，也不能轻易修改玩家机器上的其他文件或运行额外程序
- 你正在开发反作弊相关功能，希望将游戏进程降权至最低，减少攻击面

## 蓝图用法

> 本插件是纯 C++ 模块，不提供任何可直接在蓝图中调用的函数或节点。所有接口均通过 `ISecuritySandboxModule` 在 C++ 中访问。

## C++ 用法

### 头文件引入

```cpp
#include "ISecuritySandboxModule.h"
```

### 基本用法

在游戏模块（如 `UMyGameInstance`）的初始化阶段调用 `RestrictSelf()`。

```cpp
void UMyGameInstance::Init()
{
    Super::Init();
    // 检查插件是否启用，然后主动降权
    if (ISecuritySandboxModule::IsSandboxEnabled())
    {
        ISecuritySandboxModule::Get().RestrictSelf();
    }
}
```

**说明**：
- `ISecuritySandboxModule` 是单例模块接口，继承自 `ISecuritySandbox`，提供 `RestrictSelf()` 和 `IsEnabled()`。
- 若插件已被全局禁用（通过命令行 `-NoSecuritySandbox` 或构建配置），`IsSandboxEnabled()` 返回 `false`。
- `RestrictSelf()` 会永久限制进程权限，调用后无法撤销。

### 进阶用法

#### 1. 通过设置自动降权

在项目设置中（`Project Settings → Plugins → Security Sandbox`）可以配置：
- `bAutoRestrictSelf`（默认 true）：引擎初始化完成后自动调用 `RestrictSelf()`。
- `bIsEnabledByDefault`（默认 true）：决定是否无需命令行参数即可激活沙盒功能。
- `bUseLowIntegrityLevel`（Windows，默认 true）：将进程完整性级别降至低。
- `bDisallowLowIntegrityLibraries`（默认 true）：阻止加载低完整性级写入的 DLL。
- `bDisallowChildProcesses`（默认 false）：禁止创建子进程（会破坏默认崩溃报告器）。
- `bDisallowSystemOperations`（默认 false）：阻止不必要的系统操作（如注销用户、剪贴板粘贴）。

#### 2. 延迟调用（手动控制）

如果关闭自动限制，可以在关键时机（如加载第一个玩家资产之前）手动调用 `RestrictSelf()`：

```cpp
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
    // 在所有需要高权限的初始化完成之后，立即限制
    ISecuritySandboxModule::Get().RestrictSelf();
}
```

#### 3. 命令行覆盖

| 参数 | 效果 |
|---|---|
| `-WithSecuritySandbox` | 强制启用沙盒（即使设置中 `bIsEnabledByDefault=false`） |
| `-NoSecuritySandbox` | 完全禁用沙盒，忽略所有设置 |

## Demo 示例

以下是一个最小的完整示例，在自定义 `GameInstance` 中启用并调用沙盒。

**MySecurityGameInstance.h**
```cpp
#pragma once
#include "Engine/GameInstance.h"
#include "MySecurityGameInstance.generated.h"

UCLASS()
class UMySecurityGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
};
```

**MySecurityGameInstance.cpp**
```cpp
#include "MySecurityGameInstance.h"
#include "ISecuritySandboxModule.h"

void UMySecurityGameInstance::Init()
{
    Super::Init();

    // 自动限制（如果配置为自动，不重复调用）；此处是手动调用的示例
    if (ISecuritySandboxModule::IsSandboxEnabled())
    {
        ISecuritySandboxModule::Get().RestrictSelf();
        UE_LOG(LogTemp, Log, TEXT("Security sandbox restriction applied."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Security sandbox is not enabled."));
    }
}
```

**注意事项**：
- 需在项目设置中启用 `SecuritySandbox` 插件（默认不启用）。
- 模块在 `Win64` 平台下有效，其他平台编译会使用空实现（`FGenericPlatformSecuritySandbox`）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅使用标准 Core、Engine、DeveloperSettings |

（省略了几乎每个插件都依赖的 Core/CoreUObject/Engine 等。）

## 维护状态

### 近期更新

- 2024-11-10 `66e9bb39` — 移除所有 `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 作用域（代码清理）
- 2023-12-01 `6da87796` — 添加 SecuritySandbox 实验性引擎插件（首次提交）

### 维护评价

该插件自 2023-12-01 作为实验性特性首次提交后，仅有一次代码清理提交（2024-11-10）。**截至当前（2025 年 4 月），超过一年无实质性功能更新**。插件仍标记为实验性，且默认不启用。建议使用前充分测试，并在以下场景特别注意：
- 启用 `bDisallowChildProcesses` 会导致崩溃报告器失效。
- `bDisallowSystemOperations` 会阻止从其他应用粘贴内容。

对于需要高安全性的项目，可以试用，但需自行承担实验性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SecuritySandbox)
- [项目设置文档](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/SecuritySandbox/Source/SecuritySandbox/Public/SecuritySandboxSettings.h)（头文件即文档）