# Rivermax Sync

> Adding NVIDIA Rivermax synchronization capabilities for nDisplay

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 同步模块 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxSync` (Runtime), `RivermaxSyncEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-22 |
| 年龄标签 | 🆕（约 2.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync) | |

## 用途

该插件为 Unreal Engine 的虚拟制作（Virtual Production）工具链中的 **nDisplay** 系统，集成了 NVIDIA Rivermax SDK 的媒体同步能力。其核心目的是解决在 LED 墙虚拟制作或多机位实时渲染场景中，确保多个显示节点（或渲染主机）之间进行精确到帧的、时间线同步的媒体采集与输出问题。它通过提供一个基于 Rivermax 的同步策略，使得 nDisplay 集群中的所有机器能够共享一个统一的时钟源，从而实现画面撕裂消除和帧精确的同步输出。

## 使用场景

- 你正在构建一个基于 **LED 墙** 的虚拟制片摄影棚，使用 nDisplay 驱动多个渲染节点，需要确保所有节点输出的视频信号与主控信号完全同步，避免画面撕裂。
- 你需要为 nDisplay 的 **媒体输出** 功能实现一个专业的、硬件级的同步方案，替代或补充软件级的同步方法。
- 你的项目依赖 **NVIDIA Rivermax** 网络进行超低延迟的媒体数据传输，并希望与 nDisplay 的渲染流程进行深度集成和同步。

## 蓝图用法

由于插件当前主要提供底层的同步策略实现和编辑器集成，直接暴露给蓝图的交互节点较少。核心的同步策略对象 (`UMediaOutputSynchronizationPolicyRivermax`) 通常通过编辑器界面或 C++ 代码进行配置和应用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| (无直接可调用的核心函数) | 插件主要通过编辑器工厂和策略配置进行交互 | `UMediaOutputSynchronizationPolicyRivermaxFactory` |

### 使用示例（蓝图描述）

该插件通常不直接在蓝图图表中操作。主要使用流程如下：
1.  在编辑器中创建 `UMediaOutputSynchronizationPolicyRivermax` 资产。
2.  在 nDisplay 的媒体输出节点或相关配置中，选择此同步策略作为同步方法。
3.  确保 nDisplay 集群中的所有机器都正确安装并配置了 Rivermax 环境。

## C++ 用法

插件的核心功能通过 C++ 类提供，主要用于自定义或扩展同步逻辑。

### 头文件引入

```cpp
#include “MediaOutputSynchronizationPolicyRivermax.h”
```

### 基本用法

创建并应用一个 Rivermax 同步策略对象。

```cpp
// 假设在某个管理器或组件中
// 引用：基于 FactoryCreateNew 方法的典型使用模式推断
UFactory* SyncPolicyFactory = NewObject<UMediaOutputSynchronizationPolicyRivermaxFactory>();
UMediaOutputSynchronizationPolicyRivermax* RivermaxPolicy = Cast<UMediaOutputSynchronizationPolicyRivermax>(
    SyncPolicyFactory->FactoryCreateNew(
        UMediaOutputSynchronizationPolicyRivermax::StaticClass(),
        GetTransientPackage(),
        FName(“MyRivermaxSyncPolicy”),
        RF_NoFlags,
        nullptr,
        GWarn
    )
);
// 然后将 RivermaxPolicy 应用到相关的媒体输出上下文
```

### 进阶用法

继承同步策略类以实现自定义逻辑（如果基类支持）。

```cpp
UCLASS()
class UCustomRivermaxSyncPolicy : public UMediaOutputSynchronizationPolicyRivermax
{
    GENERATED_BODY()
public:
    // 可以重写虚函数以添加自定义同步校验或配置
    // virtual bool Validate() const override;
};
```

## Demo 示例

一个最小化的示例，展示如何创建并配置 Rivermax 同步策略。

```cpp
// MyRivermaxSyncManager.h
#pragma once

#include "CoreMinimal.h"
#include "MediaOutputSynchronizationPolicyRivermax.h"

class FMyRivermaxSyncManager
{
public:
    void InitializeSyncPolicy();

private:
    UPROPERTY()
    UMediaOutputSynchronizationPolicyRivermax* ActivePolicy = nullptr;
};
```

```cpp
// MyRivermaxSyncManager.cpp
#include "MyRivermaxSyncManager.h"
#include "MediaOutputSynchronizationPolicyRivermaxFactory.h"

void FMyRivermaxSyncManager::InitializeSyncPolicy()
{
    // 使用工厂创建策略实例
    UMediaOutputSynchronizationPolicyRivermaxFactory* Factory = NewObject<UMediaOutputSynchronizationPolicyRivermaxFactory>();
    if (Factory)
    {
        ActivePolicy = Cast<UMediaOutputSynchronizationPolicyRivermax>(
            Factory->FactoryCreateNew(
                UMediaOutputSynchronizationPolicyRivermax::StaticClass(),
                GetTransientPackage(),
                FName(“ActiveRivermaxPolicy”),
                RF_NoFlags,
                nullptr,
                nullptr
            )
        );

        if (ActivePolicy)
        {
            // 在此进行策略的初始参数设置
            UE_LOG(LogTemp, Log, TEXT(“Successfully created Rivermax synchronization policy.”));
        }
    }
}
```

## 模块依赖

该插件本身依赖关系明确，但其功能的完整发挥依赖于以下插件和模块：

| 模块 | 用途 |
|---|---|
| `RivermaxCore` | NVIDIA Rivermax SDK 的核心访问接口 |
| `RivermaxMedia` | 提供基于 Rivermax 的媒体读写功能 |
| `nDisplay` | 多节点渲染和显示管理系统 |
| `MediaIOCore` | 媒体输入输出核心框架（隐含依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `c7e14abd` | Rivermax: Added linux support for rivermax output | 新增 Rivermax 输出功能的 Linux 平台支持 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2025-09-18 | `d4ef24be` | Rivermax: Fix a possible mod 0 depending on cvar value. | 修复在特定控制台变量值下可能导致模 0 运算的潜在错误 |
| 2025-09-07 | `cd57697b` | Rivermax: | (提交信息不完整，推测为常规维护或小修复) |
| 2025-04-06 | `8c1407ab` | Rivermax Plugin Refactor: | 对 Rivermax 相关插件进行重构 |

### 维护评价

- **创建时间**：约 2.5 年前，属于较新的插件。
- **活跃度**：最近一次提交在 2026 年 4 月，表明仍在维护中。近期更新包括功能扩展（Linux 支持）和代码现代化（日志宏迁移），说明开发团队仍在投入资源。
- **状态**：`.uplugin` 标记为 **IsBetaVersion** 且 **EnabledByDefault** 为 false，表明它仍处于实验性阶段，可能尚未达到生产就绪的稳定性。
- **推荐**：**推荐用于实验和原型开发**。对于需要 NVIDIA Rivermax 进行精确媒体同步的 nDisplay 虚拟制片项目，这是官方提供的集成方案。但在投入关键生产环境前，应充分测试其在特定硬件和网络配置下的稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync)
- 官方文档 (无)