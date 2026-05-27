# MetaHumanRuntime

> Deprecated plugin now redirected to MetaHumanSDK

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 运行时（已废弃） |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（组件、资产重定向） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-06-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime) | |

## 用途

`MetaHumanRuntime` 是一个**已被废弃**的实验性插件。它最初被创建用于为 Unreal Engine 中的 MetaHuman 角色提供运行时组件和功能支持。其主要目标是将 `Unreal Editor for Fortnite` (UEFN) 中的 MetaHuman 组件代码进行重构和封装，形成一个基础组件类，供 UEFN 和标准 UE 版本共同使用，从而实现代码复用。

**重要提示**：此插件的所有功能已迁移并整合至 `MetaHumanSDK` 插件。使用此插件会导致加载错误，应直接使用 `MetaHumanSDK`。

## 使用场景

- 你需要为项目中的 MetaHuman 角色添加运行时交互功能。
- **强烈建议**：直接使用更新的 `MetaHumanSDK` 插件，它已取代了 `MetaHumanRuntime` 的全部功能。

## 蓝图用法

**注意**：由于此插件已被废弃且相关代码已迁移，当前版本插件内已无可用蓝图节点。以下信息基于历史提交记录，仅供参考。

### 历史节点 (已弃用)

从历史提交中推断，此插件曾提供与 MetaHuman 组件相关的蓝图节点，例如控制组件的可见性、激活状态或触发特定动画。

| 节点 | 说明 | 所在类 (历史) |
|---|---|---|
| `Set Visibility` | 设置 MetaHuman 组件的可见性 | `UMetaHumanComponentBase` |
| `Activate` | 激活或停用组件 | `UMetaHumanComponentBase` |

### 使用示例（蓝图描述）

在历史版本中，你可能会在蓝图中这样使用：
1. 从 Actor 拖拽引线，获取其 `MetaHuman Component` 组件引用。
2. 调用 `Set Visibility` 节点，并将其 `bNewVisibility` 引脚连接到一个布尔变量（例如由按键输入控制），以实现角色的显隐切换。

## C++ 用法

**注意**：此插件已被废弃，以下代码示例基于其历史设计模式，仅供参考，不应用于新项目。

### 历史头文件引入

```cpp
#include "MetaHumanComponentBase.h"
```

### 基本用法 (历史模式)

从提交历史推断，该插件的核心是 `UMetaHumanComponentBase` 类。
```cpp
// 假设在某个Actor的子类中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “MetaHuman”)
TObjectPtr<UMetaHumanComponentBase> MetaHumanComponent;
```

### 进阶用法 (历史模式)

UEFN 和 UE 的具体 MetaHuman 组件类都继承自这个基础类，重写特定功能。
```cpp
// UE版本的MetaHuman组件 (历史结构)
UCLASS(ClassGroup=(MetaHuman), meta=(BlueprintSpawnableComponent))
class UMetaHumanComponent : public UMetaHumanComponentBase
{
    GENERATED_BODY()
    // 重写或添加特定于标准UE版本的功能
};
```

## Demo 示例

一个基于历史提交的、概念性的最小示例。**此代码无法在新版引擎中直接编译，仅用于说明历史结构。**

**MetaHumanDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanDemoActor.generated.h"

class UMetaHumanComponentBase;

UCLASS()
class AMyMetaHumanActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanActor();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Components”)
    TObjectPtr<UMetaHumanComponentBase> MetaHumanRuntimeComp;
};
```

**MetaHumanDemoActor.cpp**
```cpp
#include "MetaHumanDemoActor.h"
// 注意：头文件可能已不存在
#include "MetaHumanComponentBase.h"

AMyMetaHumanActor::AMyMetaHumanActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 在历史版本中，这里会实例化具体的MetaHuman运行时组件
    MetaHumanRuntimeComp = CreateDefaultSubobject<UMetaHumanComponentBase>(TEXT(“MetaHumanComp”));
}
```

## 模块依赖

此插件本身无模块，但其功能迁移至 `MetaHumanSDK`。因此，要使用其历史功能，实际上需要依赖 `MetaHumanSDK`。

| 模块 | 用途 |
|---|---|
| `MetaHumanSDK` | 提供完整的 MetaHuman 角色运行时支持、蓝图节点和编辑器工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-16 | `62f8cc0c` | Unable to load plugin, missing dependency MetaHumanRuntime | 修复了因插件迁移导致的加载失败错误 |
| 2024-08-19 | `79003ad1` | Move MetaHumanRuntime plugin to MetaHumanSDK plugin and rename it to MetaHumanSDKRuntime | **关键变更**：将此插件正式废弃，所有功能迁移至 `MetaHumanSDK` |
| 2024-08-08 | `ea519b5c` | [MH-12702] Unreal Editor crashes after Playing a Level with an Optimized MetaHuman with MetaHuman Co | 修复了在特定配置下播放关卡导致的编辑器崩溃问题 |
| 2024-07-31 | `8e8004fd` | MetaHuman component for UE improvements | 对 UE 版本的 MetaHuman 组件进行了功能改进 |
| 2024-07-24 | `bd22b183` | Fixed issue for control rigs not running on body parts | 修复了控制绑定无法作用于身体部件的问题 |

### 维护评价

**已废弃**。此插件是实验性的，且生命周期非常短暂（从创建到废弃仅约2个月）。最后一次实质性功能更新在2024年7月底，2024年8月19日的提交正式将其标记为废弃，并将所有代码和功能转移至 `MetaHumanSDK`。后续提交仅处理因迁移引起的兼容性问题。

**强烈不推荐**在任何新项目或现有项目中使用此插件。它会导致加载错误，所有需求应通过 `MetaHumanSDK` 来满足。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime)
- [官方文档]() (暂无)
- [替代插件：MetaHumanSDK](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK)