# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 Slate 图标） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是 UE5 的实验性**高级音频事件编排与回放系统**。它解决的核心问题是：在复杂的游戏音频场景中，传统的"直接播放声音"模式难以管理大量的音效触发逻辑、参数联动和混合控制。

Subsonic 采用了**事件驱动的音频架构**：

1. **事件集合（Event Collection）**：音频设计师创建 `USubsonicEventCollection` 资产，其中定义多个"事件"（Event），每个事件可以包含多个"动作"（Action）——即具体的音频行为（播放、停止、参数变化等）。
2. **参数绑定（Parameter Binding）**：事件和集合都可以拥有参数属性包（Property Bag），蓝图中的属性可以通过绑定系统关联到音频参数，实现运行时动态控制。
3. **试听回放（Audition）**：编辑器内提供完整的试听功能，音频设计师可以在不运行游戏的情况下预览事件效果。

简单来说，Subsonic 的定位类似于 **Wwise / FMOD 的轻量内建替代方案**，为中小规模项目提供无需外部中间件的事件化音频工作流。

## 使用场景

- 你的游戏需要大量触发式音效（脚步声、环境音、UI 音效等），且希望以事件驱动方式统一管理 → 用 Subsonic Event Collection
- 你需要在编辑器中试听和调试音频事件，而不想每次都运行游戏 → 用 Subsonic 的 Audition 系统
- 你想让音频参数与游戏逻辑参数绑定（如音量随角色速度变化）→ 用 Subsonic 的 Parameter Binding
- 你不想引入外部音频中间件（Wwise/FMOD），但需要比基本 `PlaySoundAtLocation` 更结构化的音频管理 → 用 Subsonic

## 蓝图用法

> ⚠️ 当前模块（SubsonicEditor）为编辑器/运行时混合模块，核心蓝图 API 位于 SubsonicCore 和 SubsonicEngine 模块中。此处仅展示 SubsonicEditor 中暴露给蓝图的功能。

### 核心类

| 类名 | 说明 |
|---|---|
| `USubsonicEditorSubsystem` | 编辑器子系统，管理动作结构体缓存 |
| `USubsonicEventCollectionExecutor` | 事件集合执行器，用于预览和运行事件回放 |
| `USubsonicEventCollection` | 事件集合资产，定义音频事件和动作 |
| `USubsonicEventTreeView` | 事件树视图，用于编辑器 UI |
| `USubsonicEventTreeDetailsView` | 事件树详情面板视图 |
| `USubsonicCollectionParametersView` | 集合参数编辑视图 |

### 编辑器交互

Subsonic 编辑器为 `USubsonicEventCollection` 资产提供专用的资产编辑器，包含：

- **事件树面板**：以树形结构展示事件（Event）及其下属动作（Action），支持拖拽排序
- **详情面板**：编辑选中事件或动作的属性
- **参数面板**：管理集合级和事件级的参数属性包
- **试听控制栏**：播放/停止/切换试听，支持单事件预览

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicEditorSubsystem.h"
#include "SubsonicEventCollectionEditor.h"
```

### 基本用法 - 获取编辑器子系统

```cpp
// 获取 Subsonic 编辑器子系统，用于遍历所有已注册的动作结构体
USubsonicEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<USubsonicEditorSubsystem>();
if (Subsystem)
{
    // 重建动作结构体缓存（当新模块加载/卸载后调用）
    Subsystem->RebuildActionStructChildCache();
    
    // 遍历所有注册的动作结构体类型
    Subsystem->ForEachActionStruct([](const UScriptStruct& Struct)
    {
        UE_LOG(LogTemp, Log, TEXT("Registered action struct: %s"), *Struct.GetName());
    });
}
```

### 进阶用法 - 编程化操作事件集合

```cpp
// 编程化对事件集合执行撤销/重做安全的修改操作
#include "SubsonicPropertyBindingExtension.h"

USubsonicEventCollection* MyCollection = /* ... */;

// 通过事务安全的方式修改事件集合定义
UE::Subsonic::Editor::TransactEventCollection(
    NSLOCTEXT("MyApp", "AddEvent", "Add New Event"),
    *MyCollection,
    [](Core::FSubsonicEventCollectionDefinition& Definition)
    {
        // 在这里修改集合定义
        // 这个操作会被自动记录到撤销系统中
    }
);
```

### 进阶用法 - 参数绑定扩展

```cpp
// Subsonic 的参数绑定系统允许将 Property Bag 中的参数绑定到音频动作属性
// FSubsonicBindingContextStruct 扩展了标准绑定上下文，区分集合级和事件级绑定

#include "SubsonicPropertyBindingExtension.h"

// 绑定系统自动为没有 'NoBinding' 元数据标记的属性显示绑定下拉菜单
// 事件级参数如果与集合级参数类型匹配，会覆盖集合级的值
```

## Demo 示例

### 事件集合编辑器扩展

以下示例展示如何创建一个自定义的事件集合编辑器扩展：

```cpp
// MySubsonicExtension.h
#pragma once

#include "CoreMinimal.h"
#include "SubsonicEventCollection.h"

// 假设你有一个自定义的子系统需要与 Subsonic 编辑器交互
class FMySubsonicExtension
{
public:
    // 监听事件集合变更
    static void OnEventCollectionChanged(USubsonicEventCollection* Collection);
    
    // 执行事件预览
    static void PreviewEvent(USubsonicEventCollection* Collection, FName EventName);
};
```

```cpp
// MySubsonicExtension.cpp
#include "MySubsonicExtension.h"
#include "SubsonicEditorSubsystem.h"
#include "SubsonicEventCollectionEditor.h"

void FMySubsonicExtension::OnEventCollectionChanged(USubsonicEventCollection* Collection)
{
    if (Collection)
    {
        // 当事件集合内容变更后，可能需要刷新动作结构体缓存
        USubsonicEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<USubsonicEditorSubsystem>();
        if (Subsystem)
        {
            Subsystem->RebuildActionStructChildCache();
        }
    }
}

void FMySubsonicExtension::PreviewEvent(USubsonicEventCollection* Collection, FName EventName)
{
    // FEventCollectionEditor 提供了编程化的事件树选择和试听功能
    // 但通常通过编辑器 UI 操作而非直接调用
    if (Collection)
    {
        // 获取资产编辑器实例
        TArray<UObject*> Objects;
        Objects.Add(Collection);
        GEditor->GetEditorSubsystem<UAssetEditorSubsystem>()->OpenEditorForAssets(Objects);
    }
}
```

## 模块依赖

SubsonicEditor 的 Build.cs 依赖：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 核心类型定义（事件、动作、句柄） |
| `SubsonicEngine` | Subsonic 运行时引擎（执行器、回放） |
| `AudioWidgets` | 音频 UI 控件（Slate 样式继承自 FAudioWidgetsStyle） |
| `ToolMenus` | 编辑器工具栏/菜单集成 |
| `PropertyEditor` | 属性自定义和详情面板 |
| `AssetDefinition` | 资产类型定义框架 |
| `EditorFramework` | 编辑器框架（FAssetEditorToolkit） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并冲突，回退 Subsonic Subscriber 被覆盖的问题 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃导致的合并冲突 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/消除 PVS 静态分析警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单分类 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |

### 维护评价

Subsonic 是一个**实验性**插件，创建于 2026 年初，处于**活跃开发**阶段。

**优点**：
- 最近更新频繁（2026 年 4-5 月有多次提交），表明 Epic 内部正在积极开发
- 架构清晰，分为 Core/Engine/Editor/Test 四个模块，职责分离合理
- 提供了完整的编辑器工作流（事件编辑、试听、撤销/重做、参数绑定）

**注意事项**：
- ⚠️ **实验性插件**：官方明确声明不保证向后兼容性，API 可能在版本间发生破坏性变更
- ⚠️ 合并冲突修复记录表明此插件正处于频繁迭代期，可能存在不稳定因素
- 尚无官方文档（DocsURL 为空）

**推荐**：适合对音频中间件有需求且愿意接受 API 变更的团队提前探索。不建议在正式发布项目中作为核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]()（暂无）