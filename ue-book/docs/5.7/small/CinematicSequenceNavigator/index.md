# Cinematic Sequence Navigator Bridge

> Sequence Navigator Bridge for Cinematic Assemblies

| 属性 | 值 |
|---|---|
| 中文名 | 电影序列导航桥 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CinematicSequenceNavigator` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicSequenceNavigator) | |

## 用途

Cinematic Sequence Navigator Bridge 是一个**桥梁插件**，为 Unreal Engine 的 **Sequence Navigator**（序列导航器）提供对**电影级装配（Cinematic Assemblies）** 的原生支持。

标准序列导航器可以浏览、管理一般关卡序列或动画序列，但无法直接理解电影装配特有的数据组织方式（如节点层次、特殊列、保存状态）。该插件通过实现 `SequenceNavigator::FNavigationToolProvider` 的子类 `FCinematicNavigationToolProvider`，向导航器注入：

- 支持的电影序列类型（通过 `GetSupportedSequenceClasses`）
- 自定义列视图（如 ID 列）
- 工具栏按钮和上下文菜单
- 自定义拖放操作行为
- 独立的保存状态支持

简单来说，**有了这个插件，序列导航器就可以像浏览普通序列一样，直接浏览和管理电影装配中的序列**。

## 使用场景

- 你在使用 **Cinematic Assembly Tools**（电影装配工具）构建复杂的过场动画、镜头序列 → 该插件让序列导航器成为你的主要浏览和管理界面。
- 你需要在一个统一的窗口内查看所有电影装配相关的序列，并希望能按需显示 ID、名称等列，以及使用上下文菜单快速操作。
- 你希望序列导航器的状态（如展开/折叠、排序）能根据电影装配隔离保存，避免与普通序列混淆。

## 蓝图用法

该插件是纯 C++ 实现的运行时模块，**没有公开任何可被蓝图表面的函数或属性**。所有功能均通过 Sequence Navigator 的编辑器工具自动集成。你无需在蓝图中调用任何节点。

## C++ 用法

### 头文件引入

```cpp
#include "CinematicSequenceNavigatorModule.h"
#include "CinematicNavigationToolProvider.h"
```

### 基本用法

**1. 获取并激活 Provider**  
插件在 `StartupModule` 中自动监听 Sequencer 创建事件，并为每个新创建的 Sequencer 创建一个 `FCinematicNavigationToolProvider` 实例。你无需手动注册。

**2. 自定义 Provider 行为**  
如果你需要修改支持的序列类型或列，可以继承 `FCinematicNavigationToolProvider` 并覆写相应虚函数：

```cpp
// 来自 Engine/Plugins/Experimental/CinematicSequenceNavigator/Source/CinematicSequenceNavigator/Private/CinematicNavigationToolProvider.h

UCLASS(BlueprintType)
class MYCINEMATICTOOLS_API UMyMovieSceneSequence : public UMovieSceneSequence
{
    GENERATED_BODY()
    // ...
};

class FMyProvider : public UE::CineAssemblyTools::FCinematicNavigationToolProvider
{
public:
    static const FName MyIdentifier;

    FMyProvider(const TSharedRef<ISequencer>& InSequencer)
        : FCinematicNavigationToolProvider(InSequencer)
    {
    }

    virtual FName GetIdentifier() const override;
    virtual TSet<TSubclassOf<UMovieSceneSequence>> GetSupportedSequenceClasses() const override
    {
        TSet<TSubclassOf<UMovieSceneSequence>> Classes;
        Classes.Add(UMyMovieSceneSequence::StaticClass());
        return Classes;
    }
    // 其他覆写...
};
```

**3. 注册自定义 Provider**  
如果你需要在模块启动时替换或添加 Provider，可以在 `OnSequencerCreated` 回调中直接操作导航器（注意：插件本身已经注册了，一般不需要再注册）。

### 进阶用法

结合 `SequenceNavigator::INavigationTool`，你可以完全控制导航器的列、过滤、子项等。

```cpp
// 获取当前 Sequencer 对应的导航器
TSharedPtr<SequenceNavigator::INavigationTool> NavTool = GetNavigationTool();
if (NavTool.IsValid())
{
    // 获取视图模型（用于扩展列）
    SequenceNavigator::FNavigationToolColumnExtender Extender;
    // 注册自定义列
    Extender.AddColumn<FMyCustomColumn>();
    NavTool->ExtendColumns(Extender);
}
```

## Demo 示例

以下是一个最小可编译示例，展示如何检查该插件是否激活，并获取 Provider：

**CinematicNavigatorExample.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FCinematicNavigatorExampleModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**CinematicNavigatorExample.cpp**
```cpp
#include "CinematicNavigatorExample.h"
#include "CinematicSequenceNavigatorModule.h"
#include "CinematicNavigationToolProvider.h"
#include "ISequencer.h"
#include "Sequencer/Public/ISequencerModule.h"

#define LOCTEXT_NAMESPACE "FCinematicNavigatorExampleModule"

void FCinematicNavigatorExampleModule::StartupModule()
{
    // 监听 Sequencer 创建事件（与本插件的方式类似）
    ISequencerModule& SequencerModule = FModuleManager::LoadModuleChecked<ISequencerModule>("Sequencer");
    SequencerModule.RegisterOnSequencerCreated(FOnSequencerCreated::FDelegate::CreateLambda(
        [](TSharedRef<ISequencer> Sequencer)
        {
            // 检查 CinematicSequenceNavigator 插件是否提供了 Provider
            // 通过获取该 Sequencer 的 NavigationToolProvider 可以间接验证
            // 但更简单的方式：直接检查该模块是否已加载
            if (FModuleManager::Get().IsModuleLoaded("CinematicSequenceNavigator"))
            {
                UE_LOG(LogTemp, Log, TEXT("CinematicSequenceNavigator plugin is active for this Sequencer."));
            }
        }));
}

void FCinematicNavigatorExampleModule::ShutdownModule() {}

IMPLEMENT_MODULE(FCinematicNavigatorExampleModule, CinematicNavigatorExample);
#undef LOCTEXT_NAMESPACE
```

## 模块依赖

使用该插件时，你的模块的 `Build.cs` 需要添加以下依赖（省略标准引擎公共依赖）：

| 模块 | 用途 |
|---|---|
| `SequenceNavigator` | 提供导航器基础框架和 `FNavigationToolProvider` 基类 |
| `Sequencer` | 与 Sequencer 实例交互 |
| `MovieScene` | 处理电影场景序列类型 |

除此之外，该插件自身不依赖其他特殊模块。

## 维护状态

### 近期更新

- 2025-08-21 b340c11c — Sequencer: Add id column, extension  
- 2025-07-29 9a8d5bc1 — [SequenceNavigator] Refactor to use Sequencer view models and type macros  
- 2025-05-31 9ea86d8f — [SequenceNavigator] Add new CinematicSequenceNavigator plugin that implements its provider for the n...  

### 维护评价

该插件**创建于 2025 年 5 月**，截止最近一次更新（2025 年 8 月）约 3 个月的活跃开发期。目前处于 **实验性阶段**（`.uplugin` 中 `IsExperimentalVersion=true`），API 可能频繁变动，且未提供蓝图支持。功能较为专精，主要用于配合 **Cinematic Assembly Tools**。如果你正在使用电影装配工具，并且需要依赖序列导航器进行管理，这个插件是推荐的。但请注意它在生产环境中的稳定性尚未经过大规模验证，建议在非关键项目中使用或持续关注更新。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicSequenceNavigator)
- [官方文档](https://docs.unrealengine.com)（该插件暂无独立文档，请参考 Sequence Navigator 通用文档）