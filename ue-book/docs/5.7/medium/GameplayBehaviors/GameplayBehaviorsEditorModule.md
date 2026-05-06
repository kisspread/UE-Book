# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为库 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

该插件为 AI 行为树提供**即发即弃（fire-and-forget）**的行为封装。它允许开发者将独立的、可重用的逻辑片段打包成行为节点（Behavior Tasks/Decorators），并与能力系统（Gameplay Abilities）无缝协作。核心思想是简化行为树中复杂逻辑的复用，让 AI 代理可以快速触发、执行并结束特定行为，而无需维护复杂的状态机或行为树子树。

编辑器模块负责提供统一的视觉样式（Slate Style），让新建的行为节点在编辑器中拥有一致的外观和标记颜色（例如 `FGameplayBehaviorsEditorStyle::GameplayTagTypeColor`）。

## 使用场景

- 你在构建一个 AI 行为树，需要大量简短、可配置的原子行为（如“播放动画”、“发射抛体”、“启用碰撞”）。
- 你希望行为能直接启动 Gameplay Ability，并等待其完成，而无需编写额外的 BTTask 精解代码。
- 你需要快速原型化 AI 逻辑，并希望将行为视为“一次触发、自然结束”的单元。

## 蓝图用法

> 蓝图节点定义在 `GameplayBehaviorsModule`（Runtime）模块中。以下节点可直接在行为树编辑器中用于创建任务或装饰器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BTTask_GameplayBehavior` | 启动一个 GameplayBehavior 实例，等待其结束或失败 | `UBTTask_GameplayBehavior` |
| `BTTask_SetBlackboardKey`（多种类型） | 根据给定值设置黑板键值，支持所有引擎支持的黑板键类型 | `UBTTask_SetBlackboardKey*` |
| `UBTTask_GameplayBehavior_BlueprintBase` | 允许蓝图子类自定义行为逻辑 | `UBTTask_GameplayBehavior_BlueprintBase` |

### 使用示例（蓝图描述）

**创建一个即发即弃的行为：**

1. 在行为树编辑器中添加 `BTTask_GameplayBehavior` 节点。
2. 在细节面板中设置 `Behavior` 资产（一个 `UGameplayBehavior` 蓝图或类）。
3. 可选的，设置 `Blackboard Key` 以传递参数（如目标 Actor、位置等）。
4. 行为节点执行时会自动实例化并运行该行为，结束后返回 `Success`。

**在材质/蓝图中快速设置黑板值：**

`BTTask_SetBlackboardKey` 系列节点（如 `BTTask_SetBlackboardKey_Vector`, `BTTask_SetBlackboardKey_Object`）可直接在行为树中为指定黑板键赋值，无需在黑板预览面板手动修改。

## C++ 用法

### 头文件引入

```cpp
#include "GameplayBehaviorsEditorModule.h"
#include "GameplayBehaviorsEditorStyle.h"
```

### 基本用法

编辑器模块提供了单例访问入口和样式单例，可用于自定义编辑器 UI。

```cpp
// 获取编辑器模块实例
IGameplayBehaviorsEditorModule& Module = IGameplayBehaviorsEditorModule::Get();

// 获取编辑器样式对象，以读取行为标签颜色
FColor BehaviorTagColor = FGameplayBehaviorsEditorStyle::GameplayTagTypeColor;
```

### 进阶用法

在自定义的编辑器模块初始化时注册新的行为节点外观：

```cpp
void FMyEditorModule::StartupModule()
{
    FGameplayBehaviorsEditorStyle& Style = FGameplayBehaviorsEditorStyle::Get();
    // 注册自定义图标（示例）
    Style.Set("ClassThumbnail.MyCustomBehavior", new FSlateImageBrush(/*...*/));
}
```

## Demo 示例

### 最小编辑器模块（获取样式颜色）

**文件：MyEditorModule.h**

```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**文件：MyEditorModule.cpp**

```cpp
#include "MyEditorModule.h"
#include "GameplayBehaviorsEditorStyle.h"
#include "Styling/SlateStyle.h"

void FMyEditorModule::StartupModule()
{
    // 获取 AI 行为编辑器标签颜色
    FColor Color = FGameplayBehaviorsEditorStyle::GameplayTagTypeColor;
    UE_LOG(LogTemp, Log, TEXT("Gameplay Behavior Tag Color: %s"), *Color.ToString());

    // 访问样式集（可用于读取图标、字体等）
    const FSlateBrush* Brush = FGameplayBehaviorsEditorStyle::Get().GetBrush("BehaviorTreeEditor.GameplayBehavior");
    if (Brush)
    {
        // 使用该笔刷绘制自定义图标
    }
}

void FMyEditorModule::ShutdownModule()
{
    FGameplayBehaviorsEditorStyle::Shutdown();
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 行为运行时可调用能力系统（Gameplay Ability） |
| `SlateCore` | 编辑器样式集基础依赖 |
| `Slate` | 编辑器界面元素（仅编辑器模块） |
| `EditorStyle` | 编辑器全局样式（仅编辑器模块） |

> 运行时模块 `GameplayBehaviorsModule` 的依赖已在内部处理，用户只需在 `Build.cs` 中添加 `"GameplayBehaviors"` 依赖即可自动携带 `GameplayAbilities`。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 说明 |
|---|---|---|
| 2025-06-26 | `ec900998` | 为包含对应 .gen.cpp 文件的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏 |
| 2025-04-23 | `93a13080` | 使用 LyraGame 构建目标转换所有文件，为方法和静态变量添加 DLL 存储导出 |
| 2025-01-16 | `4a9936fa` | [行为树] 将黑板资产的 `ensure` 替换为错误报告，避免无效资产导致崩溃 |
| 2024-11-10 | `66e9bb39` | 移除所有 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 作用域 |
| 2024-09-27 | `58cf817b` | 为引擎中所有黑板键类型创建 `BTTask_SetKeyValueX` 节点 |

### 维护评价

- **创建时间**：2024-09-27（约 1 年）
- **更新频率**：自创建以来共有 5 次提交，最近一次在 2025-06-26（约 1 个月前），更新内容属于代码规范整理（添加生成宏、修改导出方式），说明仍在积极维护中。
- **活跃度**：维护活跃，但功能变更较少，当前主要聚焦于稳定性和引擎兼容。
- **已知问题**：实验性标签（`IsBetaVersion=true`）表明 API 可能不稳定，不建议用于正式项目中。
- **推荐使用**：适用于原型和实验性 AI 系统，生产环境需谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)（测试套件目录）