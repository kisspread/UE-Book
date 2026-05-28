# Render Grid

> Advanced pipeline for use in creating rendered cinematics.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染网格 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGrid` (Runtime), `RenderGridDeveloper` (Runtime), `RenderGridEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid) | |

## 用途

Render Grid 是一个基于蓝图的**批量过场动画渲染管理系统**，用于在编辑器中组织、预览和批量渲染多个关卡序列（Level Sequence）。它解决的核心问题是：当电影制作者需要渲染大量不同镜头/角度的过场动画时，如何高效地管理和执行这些渲染任务。

该插件在 Movie Render Queue 之上提供了一层更高级的抽象：
- 将渲染任务组织为"渲染网格作业"（Render Grid Job），每个作业绑定一个关卡序列和渲染预设
- 提供可视化的作业列表管理（添加、复制、删除、拖拽排序）
- 支持在编辑器中实时预览渲染效果（Live Preview / 单帧预览）
- 通过蓝图图编辑器实现自定义渲染逻辑
- 支持远程控制属性（Remote Control）批量调整各作业参数
- 提供渲染队列，支持暂停/恢复渲染流程

本质上，它是一个**面向电影/过场动画制作的批量渲染工作流工具**。

## 使用场景

- 你正在制作一部包含数十个镜头的过场动画，需要批量渲染所有镜头 → 用 Render Grid 管理渲染作业列表
- 你需要为每个镜头设置不同的摄像机角度、关卡序列和渲染参数 → 用 Render Grid 的作业属性面板
- 你需要在正式渲染前预览单帧效果 → 用 Render Grid 的预览渲染功能
- 你需要对多个作业批量修改相同的参数（如曝光、后期处理） → 用 Remote Control 属性源
- 你需要暂停正在进行的批量渲染，调整参数后继续 → 用渲染队列的暂停/恢复功能

## 蓝图用法

Render Grid 本身是一个蓝图资产类型（`URenderGridBlueprint`），其核心功能通过蓝图图（Graph）编写自定义逻辑实现。以下是从源码中提取的关键蓝图 API：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIsDebugging` | 设置编辑器是否进入调试模式 | `IRenderGridEditor` |
| `IsBatchRendering` | 查询是否正在批量渲染 | `IRenderGridEditor` |
| `IsPreviewRendering` | 查询是否正在预览渲染 | `IRenderGridEditor` |
| `GetBatchRenderQueue` | 获取当前批量渲染队列 | `IRenderGridEditor` |
| `GetPreviewRenderQueue` | 获取当前预览渲染队列 | `IRenderGridEditor` |
| `GetSelectedRenderGridJobs` | 获取当前选中的渲染作业列表 | `IRenderGridEditor` |
| `SetSelectedRenderGridJobs` | 设置选中的渲染作业列表 | `IRenderGridEditor` |
| `MarkAsModified` | 标记当前资产已被修改 | `IRenderGridEditor` |

### 渲染队列事件

插件提供了渲染生命周期的蓝图事件（从首次提交信息推断）：

| 事件 | 说明 |
|---|---|
| Begin Render | 批量渲染开始时触发 |
| End Render | 批量渲染结束时触发 |
| Pause | 渲染队列暂停时触发 |
| Resume | 渲染队列恢复时触发 |

### 使用示例（蓝图描述）

1. **创建 Render Grid 资产**：在内容浏览器右键 → Blueprint → 选择 `RenderGrid` 作为父类
2. **添加渲染作业**：在 Render Grid 编辑器的 Listing 模式中，使用工具栏的"Add Job"按钮添加作业
3. **配置作业参数**：在作业列表中选中作业，在右侧属性面板中设置关卡序列、输出分辨率等
4. **预览渲染**：切换到 Viewer 面板，选择 Preview 模式查看单帧预览效果
5. **批量渲染**：启用需要渲染的作业（勾选 Enabled 列），点击工具栏的"Batch Render List"按钮开始批量渲染

## C++ 用法

### 头文件引入

```cpp
#include "IRenderGridEditorModule.h"
#include "IRenderGridEditor.h"
```

### 基本用法 - 创建 Render Grid 编辑器实例

```cpp
// 通过模块接口创建渲染网格编辑器
UE::RenderGrid::IRenderGridEditorModule& EditorModule = UE::RenderGrid::IRenderGridEditorModule::Get();
TSharedRef<UE::RenderGrid::IRenderGridEditor> Editor = EditorModule.CreateRenderGridEditor(
    EToolkitMode::Standalone,
    InitToolkitHost,
    InRenderGridBlueprint
);

// 查询渲染状态
if (Editor->IsBatchRendering())
{
    URenderGridQueue* Queue = Editor->GetBatchRenderQueue();
    // 处理渲染队列...
}

if (Editor->CanCurrentlyRender())
{
    // 可以开始新的渲染
}
```

### 监听编辑器事件

```cpp
// 监听渲染网格数据变化
Editor->OnRenderGridChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Render grid data changed"));
});

// 监听作业创建
Editor->OnRenderGridJobCreated().AddLambda([](URenderGridJob* Job)
{
    UE_LOG(LogTemp, Log, TEXT("New job created: %s"), *Job->GetName());
});

// 监听作业选择变化
Editor->OnRenderGridJobsSelectionChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Job selection changed"));
});
```

### 进阶用法 - 扩展属性源部件工厂

```cpp
// 实现自定义属性源部件工厂
class FMyPropsSourceWidgetFactory : public UE::RenderGrid::IRenderGridPropsSourceWidgetFactory
{
public:
    virtual TSharedPtr<UE::RenderGrid::Private::SRenderGridPropsBase> CreateInstance(
        URenderGridPropsSourceBase* PropsSource,
        TSharedPtr<UE::RenderGrid::IRenderGridEditor> BlueprintEditor) override
    {
        // 返回自定义的属性面板部件
        return SNew(UE::RenderGrid::Private::SRenderGridPropsBase);
    }
};

// 注册工厂（通过模块扩展性管理器）
UE::RenderGrid::IRenderGridEditorModule& Module = UE::RenderGrid::IRenderGridEditorModule::Get();
// 通过菜单和工具栏扩展性管理器扩展编辑器 UI
TSharedPtr<FExtensibilityManager> MenuManager = Module.GetMenuExtensibilityManager();
TSharedPtr<FExtensibilityManager> ToolbarManager = Module.GetToolBarExtensibilityManager();
```

## Demo 示例

以下展示如何在自定义编辑器工具中集成 Render Grid：

```cpp
// MyRenderGridTool.h
#pragma once

#include "CoreMinimal.h"
#include "IRenderGridEditor.h"
#include "IRenderGridEditorModule.h"

class FMyRenderGridTool
{
public:
    void OpenRenderGridEditor(URenderGridBlueprint* Blueprint)
    {
        if (!Blueprint) return;

        UE::RenderGrid::IRenderGridEditorModule& EditorModule = 
            UE::RenderGrid::IRenderGridEditorModule::Get();
        
        Editor = EditorModule.CreateRenderGridEditor(
            EToolkitMode::Standalone,
            nullptr,
            Blueprint
        );

        // 监听选择变化
        Editor->OnRenderGridJobsSelectionChanged().AddSP(
            this, &FMyRenderGridTool::OnSelectionChanged);
    }

    TArray<URenderGridJob*> GetSelectedJobs() const
    {
        if (Editor.IsValid())
        {
            return Editor->GetSelectedRenderGridJobs();
        }
        return {};
    }

    bool CanStartRendering() const
    {
        return Editor.IsValid() && Editor->CanCurrentlyRender();
    }

private:
    void OnSelectionChanged()
    {
        // 处理选择变化逻辑
        TArray<URenderGridJob*> SelectedJobs = Editor->GetSelectedRenderGridJobs();
        UE_LOG(LogTemp, Log, TEXT("Selected %d jobs"), SelectedJobs.Num());
    }

    TSharedPtr<UE::RenderGrid::IRenderGridEditor> Editor;
};
```

## 模块依赖

> 由于缺少 Build.cs 的完整依赖信息，以下基于源码分析推断的依赖关系。使用者的模块需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `RenderGrid` | 核心运行时模块，包含渲染网格数据模型和渲染逻辑 |
| `RenderGridDeveloper` | 开发者工具模块 |
| `RenderGridEditor` | 编辑器模块，提供蓝图编辑器和 UI |
| `BlueprintEditor` | 基类 `FBlueprintEditor` 的依赖（编辑器集成） |
| `LevelSequence` | 关卡序列播放支持 |
| `RemoteControl` | 远程控制属性面板支持 |
| `AssetDefinition` | 资产定义和内容浏览器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 FSharedString 双类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |
| 2025-09-15 | `60737405` | Render Grid: fixed crash when passing in an empty string when setting remote control values | 修复设置远程控制值时传入空字符串导致的崩溃 |
| 2025-06-11 | `b57e00bc` | Replace some usages of FORCEINLINE with inline in Rendering modules. | 将渲染模块中的部分 FORCEINLINE 替换为 inline |

### 维护评价

- **创建时间**：2022 年 8 月，约 3 年前，相对较新
- **实验性状态**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，需要手动启用，API 可能不稳定
- **近期更新**：2025-2026 年间有持续的更新，但多为引擎级别的维护性修改（日志迁移、内存优化、编译修复），插件专属的功能性更新较少（2025-09-15 有一次 bug 修复）
- **维护活跃度**：⚠️ 维护中但不活跃。虽然有持续提交，但多为被动维护（跟随引擎重构），缺乏主动的功能迭代
- **风险提示**：作为实验性插件，且 `EnabledByDefault=false`，在生产环境使用需谨慎。首次提交信息（2022-08）展示了较完整的功能集，但此后未见显著功能扩展
- **推荐程度**：如果你的项目需要在编辑器内管理批量电影渲染工作流，可以尝试使用，但需注意实验性标记带来的 API 稳定性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid)
- 官方文档（无）
- [核心模块 RenderGrid](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid/Source/RenderGrid)
- [开发者模块 RenderGridDeveloper](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid/Source/RenderGridDeveloper)
- [编辑器模块 RenderGridEditor](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid/Source/RenderGridEditor)