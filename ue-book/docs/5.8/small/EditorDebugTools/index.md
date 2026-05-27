# Editor Debug Tools

> 

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器调试工具 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorDebugTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-10-19 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorDebugTools) | |

## 用途

EditorDebugTools 是一个编辑器调试 UI 集合插件，将原先分散的 Toolbox、Gamma UI 和 Module UI 整合到一个统一的插件中。该插件的目标是作为未来所有编辑器调试 UI 的统一归属地。

它提供三个核心调试面板：

1. **Module UI**：查看和管理已加载/未加载的模块，支持加载、卸载、重新加载、重新编译操作
2. **Debug Panel**：纹理重新加载、纹理图集显示、字体图集显示、字体缓存刷新、测试套件入口
3. **Gamma UI**：调节编辑器 Gamma 值的滑块面板

## 使用场景

- 你正在开发插件或修改引擎模块 → 用 Module UI 面板快速加载/卸载/重编译目标模块，无需重启编辑器
- 你怀疑纹理或字体资源出现问题 → 用 Debug Panel 重新加载纹理、查看纹理图集和字体图集、刷新字体缓存
- 你需要精确调整编辑器显示的 Gamma 值进行视觉调试 → 用 Gamma UI 面板实时调节
- 你需要运行内置测试套件验证引擎状态 → 用 Debug Panel 的 Test Suite 按钮

## 蓝图用法

该插件为纯 C++/Slate 编辑器插件，不暴露蓝图 API。

### 核心节点

无（纯编辑器 UI 插件，不提供蓝图接口）。

### 使用方式

通过编辑器菜单 **Window → EditorDebugTools** 打开插件窗口（基于 `FEditorDebugToolsCommands::OpenPluginWindow` 命令注册）。

## C++ 用法

### 头文件引入

```cpp
#include "EditorDebugTools.h"
```

### 基本用法

该插件主要通过编辑器 UI 交互使用，以下是其内部关键类的结构说明：

**Module UI（SModuleUI）** 是核心面板，提供模块管理功能：

```cpp
// 内部数据结构 - 每个模块列表项
struct FModuleListItem
{
    FName ModuleName;

    FReply OnLoadClicked();      // 加载模块
    FReply OnUnloadClicked();    // 卸载模块
    FReply OnReloadClicked();    // 重新加载模块
    FReply OnRecompileClicked(); // 重新编译模块

    // 根据模块状态控制按钮可见性
    EVisibility GetVisibilityBasedOnLoadedAndShutdownableState() const;
    EVisibility GetVisibilityBasedOnReloadableState() const;
    EVisibility GetVisibilityBasedOnRecompilableState() const;
    EVisibility GetVisibilityBasedOnUnloadedState() const;
};
```

**SDebugPanel** 提供纹理和字体相关的调试操作：

```cpp
// 来源: Source/EditorDebugTools/Private/SDebugPanel.h
class SDebugPanel : public SCompoundWidget
{
    FReply OnReloadTexturesClicked();   // 重新加载所有纹理
    FReply OnDisplayTextureAtlases();   // 显示纹理图集窗口
    FReply OnDisplayFontAtlases();      // 显示字体图集窗口
    FReply OnFlushFontCacheClicked();   // 刷新字体缓存
    FReply OnTestSuiteClicked();        // 打开测试套件
};
```

**SGammaUIPanel** 提供 Gamma 调节功能：

```cpp
// 来源: Source/EditorDebugTools/Private/GammaUIPanel.h
class SGammaUIPanel : public SCompoundWidget
{
    float OnGetGamma() const;              // 获取当前 Gamma 值
    void OnGammaChanged(float NewValue);   // Gamma 值变更回调
};
```

## Demo 示例

该插件为内部编辑器工具，无需在外部模块中集成。如需扩展开面板，可参考其 Slate 模式：

```cpp
// EditorDebugToolsCommands.h
#pragma once

#include "Framework/Commands/Commands.h"
#include "EditorDebugToolsStyle.h"

class FEditorDebugToolsCommands : public TCommands<FEditorDebugToolsCommands>
{
public:
    FEditorDebugToolsCommands()
        : TCommands<FEditorDebugToolsCommands>(
            TEXT("EditorDebugTools"),
            NSLOCTEXT("Contexts", "EditorDebugTools", "EditorDebugTools Plugin"),
            NAME_None,
            FEditorDebugToolsStyle::GetStyleSetName())
    {
    }

    virtual void RegisterCommands() override;

public:
    TSharedPtr<FUICommandInfo> OpenPluginWindow;
};
```

```cpp
// EditorDebugToolsStyle.h
#pragma once

class ISlateStyle;

class FEditorDebugToolsStyle
{
public:
    static void Initialize();
    static void Shutdown();
    static const ISlateStyle& Get();
    static FName GetStyleSetName();

private:
    static TSharedRef<class FSlateStyleSet> Create();
    static TSharedPtr<class FSlateStyleSet> StyleInstance;
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 新格式 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 适配 IsSavingPackage API 变更 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 移除大量 5.2 版本废弃的头文件包含顺序宏 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us | Slate 框架废弃 ItemHeight API，插件适配该变更 |
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化移除不必要的私有模块头文件包含和依赖 |

### 维护评价

EditorDebugTools 自 2020 年创建以来，近 5 年的更新主要集中在引擎 API 适配和编译修复，没有功能性更新。近期（2026 年）仍在跟随引擎编译基础设施变更（UE_LOGF 迁移、IsSavingPackage 适配），说明该插件仍在活跃维护中。

**优点**：
- 作为 Epic 官方维护的编辑器工具，随引擎主线同步更新
- 功能稳定，无已知严重问题
- 默认启用，对编辑器调试工作流有实际价值

**注意**：
- 功能较为基础，没有扩展机制
- 仅限 Editor 模块，不能在打包项目中使用
- 长期没有新增调试功能，可能处于"维护模式"

**推荐**：✅ 建议启用。作为默认启用的编辑器调试工具，Module UI 和纹理/字体调试功能在日常引擎开发中非常实用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorDebugTools)