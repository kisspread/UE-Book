# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 分层 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、编辑器、测试） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAF Layering 插件是 Unreal Animation Framework (UAF) 的一部分，旨在为动画系统提供一个结构化和可复用的动画层堆栈（Layer Stack）定义框架。它解决了在复杂动画管线中（如动画蒙太奇、状态机或 IK 解算）难以管理、组合和重用多个动画覆盖层的问题。通过将分层逻辑抽象为独立的“层堆栈”资产，开发者可以像编辑材质图层一样，直观地构建和调整动画覆盖关系，从而实现更灵活、更强大的角色动画控制。

## 使用场景

- 你的项目使用了复杂的 UAF 动画系统，并且需要为角色的不同部位（如上半身、下半身）或不同功能（如瞄准、受击反应）定义清晰的、可叠加的动画覆盖逻辑。
- 你希望将一系列动画覆盖规则（如 Layer Blend、IK 解算覆盖、动画遮罩）封装成一个可复用的资产，便于在不同角色或不同动画蓝图中复用。
- 你需要一个可视化的编辑器工具来设计和调试这些分层动画逻辑，而不是在动画蓝图中手动连接复杂的节点。

## 蓝图用法

### 核心节点

（注：基于模块名称和常规设计推断，具体节点名需查阅实际生成的蓝图接口。）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Layer Stack` | 创建一个新的层堆栈资产实例 | `ULayerStackFactory` |
| `Apply Layer Stack to AnimInstance` | 将指定的层堆栈资产应用到动画实例 | `ULayeringSubsystem` |
| `Set Layer Stack Property` | 设置层堆栈中特定层的属性值 | `ULayerStack` |

## C++ 用法

### 头文件引入

```cpp
#include "LayerStack.h"
#include "LayeringSubsystem.h"
```

### 基本用法

创建和访问层堆栈资产。

```cpp
// 创建一个层堆栈工厂
ULayerStackFactory* Factory = NewObject<ULayerStackFactory>();
UObject* NewAsset = Factory->FactoryCreateNew(
    ULayerStack::StaticClass(),
    Package,
    FName(“MyLayerStack“),
    RF_Public | RF_Standalone,
    nullptr,
    GWarn
);
// 来源：Tests/UAFLayeringTests.Build.cs (测试用例) 隐含的基本操作
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建和初始化一个层堆栈资产。

**LayerStackDemo.h**
```cpp
#pragma once
#include “CoreMinimal.h“
#include “LayerStack.h“
#include “LayerStackDemo.generated.h“
UCLASS()
class MYGAME_API ULayerStackDemo : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadWrite)
    ULayerStack* MyLayerStack;
    void CreateDemoLayerStack();
};
```

**LayerStackDemo.cpp**
```cpp
#include “LayerStackDemo.h“
#include “LayerStackFactory.h“
void ULayerStackDemo::CreateDemoLayerStack()
{
    ULayerStackFactory* Factory = NewObject<ULayerStackFactory>();
    MyLayerStack = Cast<ULayerStack>(Factory->FactoryCreateNew(
        ULayerStack::StaticClass(),
        GetTransientPackage(),
        FName(“DemoStack“),
        RF_Transient,
        nullptr,
        GWarn
    ));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationCore` | UAF 分层框架的核心动画基础设施 |
| `AnimGraph` | 编辑器中可视化层堆栈图的支撑 |
| `Workspace` | 提供资产工作区和编辑器集成（来自首次提交描述） |
| `UAF` (若存在) | 上层 UAF 框架的依赖（假设） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新版结构化日志系统。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名函数以更准确地反映其自动创建的功能。 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | 对分层系统进行了一次功能性更新（具体变更未说明）。 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新了 UAF 的混合配置文件。 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | 在编辑器中默认展开大纲视图的层项。 |

### 维护评价

该插件创建于 2026 年 1 月，年龄约 1 年，目前处于**实验性**阶段 (`EnabledByDefault: false`, `IsExperimentalVersion: true`)。从 git 历史看，其最近一次更新在 2026 年 4 月，期间有持续的迭代和改进，包括功能增强、接口重命名、日志系统迁移以及用户体验优化，表明该插件仍处于**活跃开发**中。作为实验性功能，其 API 和功能可能尚未稳定，不建议直接用于生产项目，但非常适合跟踪 UAF 动画系统的最新发展并进行原型开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering/Tests)