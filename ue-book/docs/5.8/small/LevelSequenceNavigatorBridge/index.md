# Level Sequence Navigator Bridge

> Sequence Navigator Bridge for Level Sequences

| 属性 | 值 |
|---|---|
| 中文名 | 关卡序列导航桥接器 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LevelSequenceNavigatorBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LevelSequenceNavigatorBridge) | |

## 用途

该插件是一个桥梁（Bridge），用于将 `ULevelSequence`（关卡序列）适配到 **Sequence Navigator**（序列导航器）工具中。Sequence Navigator 是一个用于在 Sequencer 编辑器内以树状图形式浏览和管理序列（Sequence）内元素（如轨道、片段、关键帧等）的高级工具。`LevelSequenceNavigatorBridge` 插件的核心作用是为 `Sequence Navigator` 提供一个专门针对 `ULevelSequence` 类型的数据提供者（Provider），从而使 Sequence Navigator 能够正确解析和显示 Level Sequence 内部的数据结构。

## 使用场景

- 你正在使用 Sequencer 编辑关卡序列（Level Sequence），并希望利用序列导航器（Sequence Navigator）的强大功能来以层级视图管理复杂的轨道和片段结构。
- 你需要在自定义的 Sequencer 工具中集成对 Level Sequence 的导航视图支持。

## 蓝图用法

该插件没有暴露任何蓝图可调用（`UFUNCTION(BlueprintCallable)`）的函数或蓝图可读写（`UPROPERTY(BlueprintReadWrite)`）的属性。其功能完全通过 C++ 模块在 Sequencer 初始化时自动集成。

## C++ 用法

### 头文件引入

```cpp
// 如果你需要确保此插件已加载（通常不需要，因为它默认启用）
#include "Modules/ModuleManager.h"
```

### 基本用法

该插件的核心是提供一个 `FLevelSequenceNavigationToolProvider`，它会在 `FLevelSequenceNavigatorBridgeModule` 启动时自动注册到 `Sequence Navigator` 工具的提供者管理系统中。作为插件使用者，你通常不需要直接操作它。

如果你想在自己的代码中检查或依赖此插件模块是否加载，可以使用标准模块加载方式：

```cpp
// 确保模块已加载（例如在模块依赖中声明后）
if (FModuleManager::Get().IsModuleLoaded(TEXT("LevelSequenceNavigatorBridge")))
{
    // 模块已加载
}
```

**来源文件**: `Source/LevelSequenceNavigatorBridge/Private/LevelSequenceNavigatorBridgeModule.h`

## Demo 示例

该插件本身即为 `Sequence Navigator` 的扩展提供者。以下代码展示了其内部工作原理的简化示例，说明了如何创建一个类似的导航工具提供者。

**LevelSequenceNavigationToolProvider.h**
```cpp
// (节选自 LevelSequenceNavigationToolProvider.h)
#pragma once

#include "NavigationToolDefines.h"
#include "Providers/NavigationToolProvider.h"

class FLevelSequenceNavigationToolProvider : public UE::SequenceNavigator::FNavigationToolProvider
{
public:
    static const FName Identifier;

    // 返回此提供者支持的序列类型（此处为 ULevelSequence）
    virtual TSet<TSubclassOf<UMovieSceneSequence>> GetSupportedSequenceClasses() const override;

    // 激活/停用时的逻辑
    virtual void OnActivate() override;
    virtual void OnDeactivate() override;

    // 扩展列视图、过滤器、子项等
    virtual void OnExtendColumns(...) override;
    virtual void OnExtendItemChildren(...) override;
    // ... 其他覆盖方法
};
```

**LevelSequenceNavigatorBridgeModule.cpp (示意)**
```cpp
// (示意代码，展示注册逻辑)
#include "LevelSequenceNavigatorBridgeModule.h"
#include "LevelSequenceNavigationToolProvider.h"
#include "SequenceNavigatorModule.h"

void FLevelSequenceNavigatorBridgeModule::StartupModule()
{
    // 创建提供者实例
    NavigationToolProvider = MakeShared<FLevelSequenceNavigationToolProvider>();
    
    // 监听 Sequencer 创建事件
    SequencerCreatedHandle = FSequenceNavigatorModule::Get().OnSequencerCreated().AddRaw(
        this, &FLevelSequenceNavigatorBridgeModule::OnSequencerCreated);
    SequencerClosedHandle = FSequenceNavigatorModule::Get().OnSequencerClosed().AddRaw(
        this, &FLevelSequenceNavigatorBridgeModule::OnSequencerClosed);
}

void FLevelSequenceNavigatorBridgeModule::OnSequencerCreated(const TSharedRef<ISequencer> InSequencer)
{
    // 当新的 Sequencer 实例创建时，将此提供者注册到其中
    if (NavigationToolProvider.IsValid())
    {
        FSequenceNavigatorModule::Get().RegisterProvider(InSequencer, NavigationToolProvider.ToSharedRef());
    }
}

void FLevelSequenceNavigatorBridgeModule::OnSequencerClosed(const TSharedRef<ISequencer> InSequencer)
{
    // 当 Sequencer 实例关闭时，反注册提供者
    if (NavigationToolProvider.IsValid())
    {
        FSequenceNavigatorModule::Get().UnregisterProvider(InSequencer, NavigationToolProvider.ToSharedRef());
    }
}

void FLevelSequenceNavigatorBridgeModule::ShutdownModule()
{
    // 清理委托句柄
    FSequenceNavigatorModule::Get().OnSequencerCreated().Remove(SequencerCreatedHandle);
    FSequenceNavigatorModule::Get().OnSequencerClosed().Remove(SequencerClosedHandle);
    
    NavigationToolProvider.Reset();
}
```

## 模块依赖

该插件的 `Build.cs` 文件未在此提供，但从代码实现中可以看出其依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `SequenceNavigator` | 核心目标模块，提供导航工具框架、提供者接口和管理器 |
| `MovieScene` | 提供 `UMovieSceneSequence` 基类和 `FMovieSceneEditorData` 等核心序列类型 |
| `LevelSequence` | 提供 `ULevelSequence` 类型（虽然代码中使用 `UMovieSceneSequence`，但桥接的正是该类型） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-22 | `9f83bb07` | [SequenceNavigator] Change or remove "Navigation Tool" comment references to "Sequence Navigator" for | 重命名注释，将 “Navigation Tool” 统一改为 “Sequence Navigator” |
| 2025-08-21 | `b340c11c` | Sequencer: Add id column, extension | Sequencer 集成：添加了 ID 列及其扩展 |
| 2025-07-29 | `9a8d5bc1` | [SequenceNavigator] Refactor to use Sequencer view models and type macros | 重构以使用 Sequencer 视图模型和类型宏 |
| 2025-05-19 | `a414e75c` | [Backout] - CL42636631 | 回退了编号为 CL42636631 的变更 |
| 2025-05-15 | `7cbe59b3` | [SequenceNavigator] Change to support UMovieSceneSequence instead of ULevelSequence | 将支持的序列类型从 ULevelSequence 改为更通用的 UMovieSceneSequence |

### 维护评价

- **活跃维护**: 该插件创建于 2025 年 5 月，年龄很新。在创建后不到 4 个月内有多次实质性提交，最近一次在 2025 年 9 月，表明它仍在**积极维护和迭代**中。
- **功能状态**: 从 commit 历史看，它经历了功能重构（如泛化序列类型支持）和与上层工具（Sequence Navigator）的同步更新，功能已基本稳定。
- **推荐使用**: 由于它是实验性（`IsExperimentalVersion: true`）插件，且 API 可能还在变化中，**推荐在需要探索 Sequencer 高级导航功能时使用**，但不建议用于追求绝对稳定性的生产项目关键路径。
- **注意事项**: 作为实验性插件，其接口（如 `FLevelSequenceNavigationToolProvider`）可能在未来的引擎版本中发生变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LevelSequenceNavigatorBridge)
- (无官方文档)