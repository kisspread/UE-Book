# EditorDebugTools

> 编辑器内部调试工具集，提供纹理重载、字体缓存清理、图集可视化、Gamma 校准及模块管理等开发辅助面板。

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ true |
| 包含内容 | ❌ false |
| 模块 | EditorDebugTools (Editor) |
| 创建时间 | 2020-10-19 |
| 年龄标签 | 👴 老古董（~5.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorDebugTools) | |

## 用途

EditorDebugTools 是 Epic 内部使用的编辑器调试面板插件，主要面向 **引擎 UI/Slate 开发者**。它注册了两个 Nomad Tab：

1. **Debug Tools** — 包含 SDebugPanel（Slate 调试按钮）和 SGammaUIPanel（Gamma 校准滑块）
2. **Modules** — SModuleUI 模块浏览器，可实时 Load / Unload / Reload / Recompile 任意模块

这个插件的核心价值在于为 Slate 框架开发者提供快速调试手段：重载纹理资源、刷新字体缓存、查看纹理/字体图集、运行 Slate Test Suite，以及在编辑器运行时动态管理模块生命周期。普通项目开发中很少直接用到，但如果你在做引擎层面的 UI 开发或排查 Slate 渲染问题，它是非常实用的工具。

## 使用场景

- 你正在开发自定义 Slate 控件，需要反复测试渲染效果 → 打开 **Debug Tools** 面板，点击 "Reload Textures" 或 "Flush Font Cache" 即时刷新
- 你需要排查字体渲染异常（如字符缺失、模糊）→ 点击 "Display Font Atlases" 查看字体图集的实际打包情况
- 你需要排查 UI 纹理异常（如图集溢出、错误的纹理引用）→ 点击 "Display Texture Atlases" 查看 Slate 纹理图集
- 你需要测试 Slate 控件的视觉表现 → 点击 "Display Test Suite" 打开内置的 Slate 测试套件（含 StarshipSuite）
- 你正在开发引擎模块，需要在编辑器运行时动态加载/卸载/重编译模块 → 打开 **Modules** 面板
- 你需要校准显示器 Gamma → 使用 Debug Tools 面板底部的 Gamma 滑块（范围 1.0 ~ 3.0）

## 蓝图用法

此插件不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它是一个纯编辑器 UI 插件，所有功能通过 Slate 面板交互操作，无法在蓝图中调用。

## C++ 用法

此插件的公共 API 非常有限——`FEditorDebugToolsModule` 仅实现 `IModuleInterface`，没有导出供外部调用的函数。其内部功能（如模块的 Load/Unload/Reload/Recompile）通过 `GEngine->DeferredCommands` 和 `IHotReloadInterface` 实现，属于编辑器内部机制。

如果需要在自己的编辑器工具中调用类似功能，可以直接使用引擎提供的模块管理 API：

### 头文件引入

```cpp
#include "Modules/ModuleManager.h"
#include "Misc/HotReloadInterface.h"
```

### 动态加载/卸载模块（参考 SModuleUI 实现）

```cpp
// 动态加载模块
GEngine->DeferredCommands.Add(FString::Printf(TEXT("Module Load %s"), *ModuleName.ToString()));

// 动态卸载模块
GEngine->DeferredCommands.Add(FString::Printf(TEXT("Module Unload %s"), *ModuleName.ToString()));

// 动态重载模块
GEngine->DeferredCommands.Add(FString::Printf(TEXT("Module Reload %s"), *ModuleName.ToString()));
```

### 热重编译模块（参考 SModuleUI::FModuleListItem::OnRecompileClicked）

```cpp
// 通过 HotReload 接口重编译模块
IHotReloadInterface& HotReloadSupport = FModuleManager::LoadModuleChecked<IHotReloadInterface>("HotReload");
bool bSuccess = HotReloadSupport.RecompileModule(
    ModuleName,
    *GLog,
    ERecompileModuleFlags::ReloadAfterRecompile | ERecompileModuleFlags::FailIfGeneratedCodeChanges
);
```

### 重载 Slate 纹理和字体缓存（参考 SDebugPanel 实现）

```cpp
// 重载所有 Slate 纹理资源
FSlateApplication::Get().GetRenderer()->ReloadTextureResources();

// 刷新字体缓存
FSlateApplication::Get().GetRenderer()->FlushFontCache(TEXT("MyDebugTool"));
```

## Demo 示例

此插件是 Editor-only 的 Slate UI 插件，不提供可复用的组件或 API。典型用法是在编辑器中直接打开面板：

1. 启动 Unreal Editor
2. 菜单栏 → **Window → Developer Tools → Debug Tools**（打开 Debug Tools 面板）
3. 菜单栏 → **Window → Developer Tools → Modules**（打开 Modules 面板）

这两个 Tab 以 Nomad Tab 方式注册，可以停靠在编辑器任意位置。

## 模块依赖

此插件本身是 Editor-only 的，不会被打包到最终游戏。如果你想在自己的编辑器工具中实现类似功能，参考以下依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块（公共依赖） |
| `Projects` | 插件管理，获取插件路径 |
| `InputCore` | 输入核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（GEngine、UPackage 等） |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `SourceCodeAccess` | 源码访问接口（判断是否可重编译） |
| `WorkspaceMenuStructure` | 开发者工具菜单分类 |
| `AppFramework` | 应用框架 |
| `SlateReflector` | Slate 调试可视化（非 Shipping 构建，动态加载） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-12-12 | `4e81c375` | Slate: Show TestSuite Button | 新增 "Display Test Suite" 按钮，可打开 Slate 内置测试套件。**最近一次功能性更新。** |
| 2024-10-22 | `98a8e0ed` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 代码清理，移除废弃的头文件包含顺序宏。纯维护性改动。 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight... | 跟随 Slate API 变更适配，UE-210415 相关。被动适配，非主动功能更新。 |

### 维护评价

- **创建时间**：2020-10-19，约 5.5 年前
- **最近功能性更新**：2024-12-12（约 1.5 年前），新增了 Test Suite 按钮
- **维护频率**：低频，每年 1-2 次改动，多为被动适配 Slate API 变更
- **稳定性**：插件功能简单且成熟，代码量小（11 个源文件），不太需要频繁更新
- **定位**：引擎内部调试工具，面向 Epic 内部 Slate 开发者，非面向普通项目开发者

**评价**：这是一个非常稳定的小型工具插件，功能自 2020 年以来几乎没有变化（除了 2024 年底新增的 Test Suite 按钮）。虽然更新不频繁，但因为功能足够简单且依赖引擎核心 API，不存在明显的废弃风险。对于需要调试 Slate 渲染问题的开发者来说仍然有用。

⚠️ 注意：此插件的公共 API 几乎为零，不适合作为其他插件的依赖。它是一个纯 UI 工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorDebugTools)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无（此插件没有对应的自动化测试）
