# InstancedActors

> 实例化Actor的引擎级插件桩。

| 属性 | 值 |
|---|---|
| 中文名 | 实例化演员 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `InstancedActors` (Runtime), `InstancedActorsTestSuite` (UncookedOnly), `InstancedActorsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-10 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors) | |

## 用途

该插件提供了一种将常规的 `AActor` 转换为**实例化Actor (Instanced Actor)** 的机制，旨在优化大量重复物体的渲染与管理性能。它并非一个独立的渲染系统，而是作为一个**适配层**，将标准的 Actor 逻辑与 **Mass 实体系统 (MassGameplay)** 的实例化能力相结合。

其核心解决的问题是：在拥有成千上万个相似物体（如树木、岩石、NPC群体）的开放世界中，为每个物体创建一个独立的 AActor 会导致极高的内存开销和 CPU 游戏线程负担。通过将这些物体转换为实例化表示，可以利用 Mass 系统的高效数据布局和批处理能力，从而显著提升游戏性能。

## 使用场景

- 你在开发一个开放世界游戏，场景中遍布着大量的树木、灌木、岩石和建筑装饰物。
- 你需要让成群的敌人或友方NPC（如市民、士兵）在场景中移动，同时保持较低的 CPU 开销。
- 你希望将现有的、基于 AActor 构建的游戏逻辑，以较低成本迁移到基于 Mass 的高性能实体架构上。
- 你正在使用或评估 MassGameplay 插件，并需要一个便捷的工具来将现有资产进行实例化转换。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Instance Handle (by Index)` | 通过索引从实例化数据中获取一个特定实例的句柄，用于后续操作。 | `UInstancedActorsEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **转换场景中的 Actor**：在编辑器关卡视口中，选中一个或多个同类 AActor（例如一片区域内的所有树）。右键点击，在上下文菜单中寻找插件提供的“**Convert Actors to Instanced Actors**”选项。这会将选中的 Actor 转换为受 `AInstancedActorsManager` 管理的实例化表示。
2.  **通过蓝图查询实例**：在一个 `UEditorSubsystem` 上下文中（如 `BeginPlay`），使用 `UInstancedActorsEditorSubsystem::GetInstanceHandle` 节点。你需要提供对应的 `UInstancedActorsData` 资产和一个整数索引，来获取特定实例的句柄，该句柄可用于触发实例相关的事件或状态查询。

## C++ 用法

### 头文件引入

```cpp
#include "InstancedActorsEditorModule.h"
#include "InstancedActorsSubsystem.h" // 用于 IASubsystemClass
```

### 基本用法

（来自 `FInstancedActorsEditorModule::CustomizedConvertActorsToIAsUIAction`）

该函数允许你通过代码调用转换流程，并可以指定使用哪个子系统类。

```cpp
// 在某个编辑器工具或上下文中
void ConvertSelectedToInstanced()
{
    // 假设已经获取到了选中的 Actor 数组 SelectedActors
    TArray<AActor*> SelectedActors = GetSelectedActors();

    // 获取编辑器模块
    FInstancedActorsEditorModule& EditorModule = FModuleManager::GetModuleChecked<FInstancedActorsEditorModule>("InstancedActorsEditor");

    // 调用转换，使用默认的子系统
    // 第二个参数可以指定一个 UInstancedActorsSubsystem 的子类，如果为空则使用默认的
    EditorModule.CustomizedConvertActorsToIAsUIAction(SelectedActors, nullptr);
}
```

### 进阶用法

（来自 `FInstancedActorsEditorModule::SetActorToIADelegate`）

你可以自定义转换逻辑，替换掉默认的转换行为。

```cpp
// 定义自己的转换逻辑
FInstancedActorsEditorModule::FOnConvert MyConvertDelegate;
MyConvertDelegate.BindLambda([](TConstArrayView<AActor*> InActors)
{
    UE_LOG(LogTemp, Log, TEXT("My Custom Conversion: Converting %d actors"), InActors.Num());
    // ... 你的自定义转换逻辑 ...
});

// 获取编辑器模块并覆盖默认行为
FInstancedActorsEditorModule& EditorModule = FModuleManager::GetModuleChecked<FInstancedActorsEditorModule>("InstancedActorsEditor");
EditorModule.SetActorToIADelegate(MyConvertDelegate, FTextFormat::FromString(TEXT("Custom Convert {0} to IA")));

// 当需要恢复默认时
// EditorModule.ResetConversionDelegates();
```

## Demo 示例

一个展示如何注册自定义转换委托的最小编辑器工具模块。

**MyInstancedActorsTool.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyInstancedActorsToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnConvertRequest(TConstArrayView<AActor*> InActors);
};
```

**MyInstancedActorsTool.cpp**
```cpp
#include "MyInstancedActorsTool.h"
#include "InstancedActorsEditorModule.h"

void FMyInstancedActorsToolModule::StartupModule()
{
    // 延迟一帧注册，确保 InstancedActorsEditor 模块已加载
    FCoreDelegates::OnPostEngineInit.AddLambda([this]()
    {
        if (FModuleManager::Get().IsModuleLoaded("InstancedActorsEditor"))
        {
            FInstancedActorsEditorModule& IaEditor = FModuleManager::GetModuleChecked<FInstancedActorsEditorModule>("InstancedActorsEditor");
            // 设置自定义的“Actor 转 IA”委托
            FInstancedActorsEditorModule::FOnConvert Delegate;
            Delegate.BindRaw(this, &FMyInstancedActorsToolModule::OnConvertRequest);
            IaEditor.SetActorToIADelegate(Delegate);
        }
    });
}

void FMyInstancedActorsToolModule::ShutdownModule()
{
    // 模块关闭时重置委托，避免悬空引用
    if (FModuleManager::Get().IsModuleLoaded("InstancedActorsEditor"))
    {
        FInstancedActorsEditorModule& IaEditor = FModuleManager::GetModuleChecked<FInstancedActorsEditorModule>("InstancedActorsEditor");
        IaEditor.ResetConversionDelegates();
    }
}

void FMyInstancedActorsToolModule::OnConvertRequest(TConstArrayView<AActor*> InActors)
{
    UE_LOG(LogTemp, Display, TEXT("My Tool: Handling conversion of %d actors."), InActors.Num());
    // 在这里实现你的自定义转换逻辑，或者调用原始的转换逻辑
    // ...
}

IMPLEMENT_MODULE(FMyInstancedActorsToolModule, MyInstancedActorsTool)
```

## 模块依赖

该插件**依赖于**以下非标准模块，使用前需确保它们已启用或存在于你的项目中：

| 模块 | 用途 |
|---|---|
| `MassGameplay` | 提供核心的 Mass 实体框架，InstancedActors 是建立在此之上的应用层。 |
| `DataRegistry` | 可能用于管理实例化Actor的模板数据和配置。 |
| `GameFeatures` | 插件架构可能依赖于Game Features系统进行功能模块化管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `16c20541` | Update Intel OneAPI supported version to 2026.0.0 | 更新了支持的Intel OneAPI工具链版本。 |
| 2026-05-12 | `865421ee` | [Mass] PR #12790: InstancedActors: Use Correct Collision CVar In All Net Modes | 修复了在不同网络模式下碰撞相关控制台变量（CVar）使用错误的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版UE_LOG日志宏迁移至新版UE_LOGF宏。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 重构了MassCore模块的头文件目录结构。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从MassEntity中提取出独立的MassCore模块。 |

### 维护评价

- **状态**：**活跃维护**。该插件作为Mass生态系统的关键组成部分，近期（截至2026年5月）仍在进行功能性更新和Bug修复。
- **趋势**：近期提交主要围绕底层Mass框架的重构和适配，以及该插件自身的特定修复，表明它与引擎核心开发保持同步。
- **推荐度**：**推荐用于特定场景**。如果你的项目大量使用Mass系统或对高性能实例化有明确需求，这是一个值得探索和使用的实验性功能。但由于其`IsExperimentalVersion=true`且默认禁用，意味着API可能不稳定，生产环境使用需谨慎评估风险。
- **警告**：该插件为实验性功能，可能在未来版本中发生重大变更或被移除。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors/Source/InstancedActorsTestSuite)