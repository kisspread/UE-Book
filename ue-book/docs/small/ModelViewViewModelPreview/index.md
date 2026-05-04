# UMG Viewmodel for UMG Preview

> A plugin to support UMG MVVM within the UMG Widget Preview plugin.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | ModelViewViewModelPreview (Editor) |
| 创建时间 | 2024-08-07 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ModelViewViewModelPreview) | |

## 用途

这个插件为 **UMG Widget Preview** 编辑器添加了 **MVVM ViewModel 预览** 功能。

在 UE5 的 MVVM 框架中，UMG Widget 可以通过 ViewModel 模式绑定数据源。当你在 Widget Preview 编辑器中预览 UMG Widget 时，原本只能看到 Widget 本身的外观，但看不到它绑定的 ViewModel 数据源。这个插件的作用就是在 Widget Preview 编辑器中新增一个 **"Viewmodels" 面板**，让你能在预览 Widget 的同时查看和选择该 Widget 绑定的所有 ViewModel Source 对象。

具体来说，这个插件：
- 通过 `IUMGWidgetPreviewModule` 的扩展接口注册一个新的编辑器标签页
- 创建一个 `SPreviewSourcePanel` 面板，列出当前预览 Widget 的所有 MVVM View Source
- 支持双向选择同步——在 Viewmodels 面板中选择一个 Source，Widget Preview 编辑器的对象选择也会同步更新（反之亦然）
- 当 Widget 重新实例化时，自动刷新 Source 列表
- 如果启用了 `UE_WITH_MVVM_DEBUGGING`，还会监听 Source 值变化并实时更新面板

## 使用场景

- 你在用 UE5 的 MVVM 框架开发 UI，想要在 Widget Preview 中查看 Widget 绑定了哪些 ViewModel → 启用此插件
- 你在调试 MVVM 数据绑定，想确认绑定的 Source 对象是否正确 → 在 Viewmodels 面板中查看 Source 列表
- 你想在预览时快速切换选中不同的 ViewModel Source 对象来检查其属性 → 在 Viewmodels 面板中点击即可

## 蓝图用法

此插件没有提供任何蓝图节点。它是一个纯编辑器 UI 扩展，所有功能都通过 Widget Preview 编辑器中的面板来使用。

## C++ 用法

此插件没有公共 API。它是一个纯编辑器扩展插件，所有类都在 `Private` 命名空间中，不对外暴露。

### 架构说明

如果你想了解或参考这个插件的扩展机制：

```
ModelViewViewModelPreviewModule（模块入口）
    ↓ 启动时加载 UMGWidgetPreview 模块
    ↓ 创建 FMVVMWidgetPreviewExtension 并注册
    
FMVVMWidgetPreviewExtension（扩展注册器）
    ↓ 监听 OnRegisterTabsForEditor 事件
    ↓ 注册 "Viewmodels" 标签页
    ↓ 使用 LayoutExtender 将标签页放在 Details 标签页之后
    ↓ 创建 SPreviewSourcePanel 作为标签页内容
    
SPreviewSourcePanel（面板 UI）
    ↓ 从 UMVVMSubsystem 获取 Widget 的 MVVM View
    ↓ 遍历 View 的所有 Source
    ↓ 在列表中显示每个 Source 的图标和名称
    ↓ 支持选择同步
```

### 关键代码片段

```cpp
// 获取 Widget 的 MVVM View（来自 SMVVMPreviewSourcePanel.cpp）
if (const UUserWidget* NewWidget = Preview->GetWidgetInstance())
{
    if (UMVVMView* View = UMVVMSubsystem::GetViewFromUserWidget(NewWidget))
    {
        for (const FMVVMView_Source& ViewSource : View->GetSources())
        {
            FName SourceName = View->GetViewClass()->GetSource(ViewSource.ClassKey).GetName();
            // SourceName 是绑定的属性名
            // ViewSource.Source 是实际的 UObject 实例
        }
    }
}
```

```cpp
// 注册扩展标签页（来自 MVVMWidgetPreviewExtension.cpp）
InPreviewEditor->GetLayoutExtender()->ExtendLayout(
    GetDetailsTabID(),  // 相对于 Details 标签页
    ELayoutExtensionPosition::After,  // 放在后面
    PreviewSourceTab
);
```

## Demo 示例

此插件没有独立的 Demo。使用方式如下：

### 启用插件

1. 打开 UE5 编辑器
2. 进入 **Edit → Plugins**
3. 搜索 **"ModelViewViewModelPreview"** 或 **"UMG Viewmodel for UMG Preview"**
4. 启用该插件（需要同时启用 **ModelViewViewModel** 和 **UMG Widget Preview** 插件）
5. 重启编辑器

### 使用面板

1. 打开一个使用了 MVVM 绑定的 UMG Widget
2. 在 Widget Preview 编辑器中预览该 Widget
3. 在编辑器标签页栏中找到 **"Viewmodels"** 标签页（默认位于 Details 标签页旁边）
4. 点击打开 Viewmodels 面板
5. 面板中会列出该 Widget 绑定的所有 ViewModel Source
6. 点击列表中的某个 Source，Details 面板会显示该 Source 对象的属性

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `InputCore` | 输入系统 |
| `Projects` | 插件管理 |
| `AdvancedWidgets` | 高级 Widget（如 SFieldIcon） |
| `ModelViewViewModel` | MVVM 核心框架 |
| `ModelViewViewModelBlueprint` | MVVM 蓝图支持 |
| `UMGWidgetPreview` | Widget Preview 编辑器（被扩展的目标） |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ModelViewViewModel` | MVVM 核心功能 |
| `UMG Widget Preview` | 被扩展的 Widget 预览编辑器 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024-11-22 | `188abffc` | Updated uplugin descriptor files marked as both Experimental and Beta | 批量更新 uplugin 描述符，将同时标记为 Experimental 和 Beta 的插件统一分类。此插件被标记为 Beta |
| 2024-08-07 | `6f984f4c` | [UMG MVVM] Uses new UMG Preview plugin | 初始提交，创建了此插件，将 MVVM 预览功能从旧的预览系统迁移到新的 UMG Widget Preview 插件架构 |

### 维护评价

- **创建时间**: 2024-08-07（不到 2 年）
- **Beta 状态**: `.uplugin` 中 `IsBetaVersion: true`，`EnabledByDefault: false`
- **最近更新**: 2024-11-22（约 1.5 年前），但该更新仅是 uplugin 描述符的批量修改，不是功能性更新
- **实质性最后更新**: 2024-08-07（初始提交，约 1.5 年前）
- **维护评价**: ⚠️ **维护不活跃** — 自创建以来没有功能性更新。插件功能简单且完整，但作为 Beta 插件长期没有更新，可能被 Epic 搁置
- **是否推荐使用**: 如果你在使用 UE5 的 MVVM 框架，这个插件对调试非常有用，可以放心启用。但由于是 Beta 状态，未来 API 可能变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ModelViewViewModelPreview)
- [ModelViewViewModel 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ModelViewViewModel)（MVVM 核心框架）
- [UMG Widget Preview 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UMGWidgetPreview)（被扩展的预览编辑器）
- 未找到独立测试用例
