# Level Sequence Navigator Bridge

> Sequence Navigator Bridge for Level Sequences

| 属性 | 值 |
|---|---|
| 中文名 | 关卡序列导航桥 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LevelSequenceNavigatorBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LevelSequenceNavigatorBridge) | |

## 用途

本插件为 **Level Sequence**（关卡序列）与 **Sequence Navigator**（序列导航器）之间提供了桥接支持。Sequence Navigator 是 UE5 中一个用于浏览、管理和交互所有类型序列（如 Blueprint Sequence、Level Sequence）的工具。该插件扩展了 Sequence Navigator，使其能够识别并正确展示 `ULevelSequence` 内容，包括：

- 提供自定义的列视图（如默认列 `AnimationColumnViewName`）
- 注册基于 `FMovieSceneEditorData` 的过滤/排序逻辑
- 绑定命令（快捷键）
- 支持保存/恢复导航状态

简单说：没有这个插件，Level Sequence 可能在 Sequence Navigator 中不可见或缺少必要的浏览功能；有了它，开发者可以在统一的导航工具中无缝浏览和操作关卡序列。

## 使用场景

- 你在项目中大量使用 **Level Sequence** 制作过场动画或交互事件，需要一种高效的方式来浏览、搜索、切换多个序列资产。
- 你正在开发一个使用 **Sequence Navigator** 的自定义编辑器工具，需要让其支持 Level Sequence 类型。
- 你需要为 Level Sequence 添加额外的列（如镜头、音效等），利用插件提供的 `OnExtendColumns` 回调进行扩展。

## 蓝图用法

本插件是纯 C++ 编辑器模块，未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有功能仅在编辑器环境中通过扩展点生效，无法在蓝图节点中直接调用。

## C++ 用法

### 头文件引入

```cpp
#include "LevelSequenceNavigatorBridgeModule.h"
#include "LevelSequenceNavigationToolProvider.h"
```

### 基本用法

插件在模块启动时自动注册 `FLevelSequenceNavigationToolProvider` 到 Sequence Navigator 系统。您无需手动注册或配置。如果您需要自定义行为，可以继承 `FLevelSequenceNavigationToolProvider` 并重写其虚方法。

```cpp
// 在自定义模块中获取已注册的协议器
void UMySequenceUtils::SetupCustomProvider()
{
    // 获取插件模块并访问内部 provider（不推荐直接依赖内部细节）
    // 推荐做法：通过 INavigationTool 接口扩展
    auto& BridgeModule = FModuleManager::LoadModuleChecked<FLevelSequenceNavigatorBridgeModule>("LevelSequenceNavigatorBridge");
    // 通常无需直接操作 provider，而是使用 Sequence Navigator 的公开 API
}
```

更常见的用法是在自己的插件/模块中 **扩展** 由该 provider 提供的列或过滤条件：

```cpp
// 在您的代码中监听 OnExtendColumns 事件（需要引用 SequenceNavigator 的接口）
#include "NavigationToolProvider.h"
#include "LevelSequenceNavigationToolProvider.h"

void MyExtension::Setup()
{
    // 假设您有一个 INavigationTool 实例
    FNavigationToolColumnExtender Extender;
    Extender.OnExtendColumn.BindStatic(&MyColumnCallback);
    // 将该 Extender 注册到导航工具
}
```

### 进阶用法

如果您需要为 Level Sequence 增加自定义子项（比如显示关卡内的子对象或标记），可以重写 `OnExtendItemChildren` 方法。示例重写（在您继承的 Provider 中）：

```cpp
void FMyLevelSequenceProvider::OnExtendItemChildren(
    UE::SequenceNavigator::INavigationTool& InTool,
    const UE::SequenceNavigator::FNavigationToolViewModelPtr& InParentItem,
    TArray<UE::SequenceNavigator::FNavigationToolViewModelWeakPtr>& OutWeakChildren,
    const bool bInRecursive)
{
    // 调用父类实现基础逻辑
    FLevelSequenceNavigationToolProvider::OnExtendItemChildren(InTool, InParentItem, OutWeakChildren, bInRecursive);

    // 自定义：如果是某个特定 Level Sequence，添加一个子项
    // ...
}
```

## Demo 示例

由于插件本身即为最小功能单元，无需额外创建完整示例。若需测试插件功能，只需在编辑器内打开 **Sequence Navigator** 面板（若未启用，需在窗口菜单中打开），确认 Level Sequence 资产已正确显示并能展开浏览。同时可在序列导航器设置中查看默认列（如“Animation”列）。

## 模块依赖

本插件编译时依赖以下模块（仅列出非标准模块，省略 Core/Engine/Editor 系列）：

| 模块 | 用途 |
|---|---|
| `SequenceNavigator` | 提供导航工具框架及 `FNavigationToolProvider` 基类 |
| `Sequencer` | 提供 `ISequencer` 接口，用于监听序列创建/关闭事件 |
| `MovieScene` | 处理 `UMovieSceneSequence` 及其 `FMovieSceneEditorData` |
| `LevelSequence` | 核心资产类型 `ULevelSequence` 及其相关 API |
| `UnrealEd` | 编辑器常用基础设施 |

## 维护状态

### 近期更新

- 2025-08-21 b340c11c Sequencer: Add id column, extension
- 2025-07-29 9a8d5bc1 [SequenceNavigator] Refactor to use Sequencer view models and type macros
- 2025-05-19 a414e75c [Backout] - CL42636631
- 2025-05-15 7cbe59b3 [SequenceNavigator] Change to support UMovieSceneSequence instead of ULevelSequence
- 2025-05-14 55054d5d [SequenceNavigator] Move Level Sequence Navigator to LevelSequenceNavigatorBridge plugin

### 维护评价

该插件创建于 2025 年 5 月，属于非常新的实验性插件。从提交记录来看，过去 3 个月内有多次实质性更新：重构支持 ViewModel、增加 ID 列等，表明 **积极维护中**。由于仍标注为实验性，API 和功能可能会随时间变化，但推荐在需要使用 Sequence Navigator 浏览 Level Sequence 的场景中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LevelSequenceNavigatorBridge)
- [官方文档]（暂缺）