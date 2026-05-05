# Actor Palette

> Allows creation of Actor Palettes based on existing levels to quickly select actors and drag them into the level editor

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | ActorPalette (Editor) |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ActorPalette) | |

## 用途

Actor Palette 是一个编辑器工具，让你把任意已有的 Level（关卡）当作"Actor 资源库"来使用。它在一个独立的 Viewport 面板中加载指定关卡，你可以浏览关卡中放置好的 Actor（比如各种 Mesh、蓝图实例等），然后通过拖拽直接将它们的关联资产放入当前编辑的关卡中。

核心工作原理：插件使用 `ULevelStreamingDynamic::LoadLevelInstance` 将目标关卡动态加载到一个独立的 `FPreviewScene` 中，然后通过自定义的 `FEditorViewportClient` 拦截鼠标拖拽操作，生成 `FAssetDragDropOp` 拖拽事件，让你可以把 Actor 引用的资产（如 Static Mesh）拖到主编辑器窗口中。

这本质上是一个"模板关卡浏览器"——你可以预先在某个关卡中精心摆放好各种道具、建筑部件、装饰物，然后在做关卡设计时随时打开这个关卡作为素材库，拖拽放置。

## 使用场景

- 你有一个"素材库关卡"，里面摆放了项目中常用的建筑部件、道具、装饰物 → 用 Actor Palette 打开它，直接拖拽到正在编辑的关卡中
- 你在做关卡设计（Level Design），需要频繁从多个预设关卡中挑选 Actor 放置 → 开多个 Actor Palette Tab，分别打开不同的素材关卡
- 你想快速浏览某个关卡中有哪些 Actor 可以复用 → 用 Actor Palette 打开浏览，Game View 模式下可以看到实际渲染效果

## 蓝图用法

此插件不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它是一个纯编辑器 UI 工具，所有交互都在编辑器面板中完成。

## C++ 用法

此插件是纯编辑器工具，没有面向使用者的公共 C++ API。以下内容面向想要理解或扩展插件内部实现的开发者。

### 头文件引入

```cpp
#include "ActorPaletteModule.h"
#include "ActorPaletteViewportClient.h"
```

### 内部架构

插件由以下几个核心类组成：

| 类 | 文件 | 职责 |
|---|---|---|
| `FActorPaletteModule` | ActorPaletteModule.h/cpp | 模块入口，注册最多 4 个 NomadTab Spawner |
| `SActorPalette` | ActorPalette.h/cpp | 顶层 Slate Widget，组合 Viewport 和 ViewportClient |
| `SActorPaletteViewport` | ActorPaletteViewport.h/cpp | 继承 `SEditorViewport`，提供标准编辑器视口 + 工具栏 |
| `FActorPaletteViewportClient` | ActorPaletteViewportClient.h/cpp | 继承 `FEditorViewportClient`，管理 PreviewScene、关卡流式加载、拖拽操作 |
| `UActorPaletteSettings` | ActorPaletteSettings.h/cpp | 继承 `UDeveloperSettings`，持久化存储最近使用/收藏的关卡列表 |
| `FActorPaletteCommands` | ActorPaletteCommands.h/cpp | 注册快捷键命令（G = Game View，无默认快捷键 = Reset Camera） |
| `FActorPaletteStyle` | ActorPaletteStyle.h/cpp | Slate 样式定义（图标、文字样式等） |

### 关键实现细节

**关卡加载**（`FActorPaletteViewportClient::OpenWorldAsPalette`）：

```cpp
// 使用 ULevelStreamingDynamic 将目标关卡流式加载到 PreviewScene 中
ULevelStreamingDynamic* NewLevel = ULevelStreamingDynamic::LoadLevelInstance(
    TargetWorld, SourceWorld->GetPathName(),
    FVector::ZeroVector, FRotator::ZeroRotator, bSucceeded);

// RenameForPIE 是一个 workaround，避免关卡名冲突
NewLevel->RenameForPIE(1);

// 加载完成后重置相机到关卡的编辑器视图位置
TargetWorld->EditorViews = SourceWorld->EditorViews;
ResetCameraView();
```

**拖拽生成**（`FActorPaletteViewportClient::InputKey`）：

```cpp
// 检测鼠标拖拽命中了哪个 Actor
HHitProxy* HitProxy = InEventArgs.Viewport->GetHitProxy(HitX, HitY);
if (HActor* ActorProxy = HitProxyCast<HActor>(HitProxy))
{
    // 获取 Actor 引用的内容资产（如 StaticMesh）
    TArray<UObject*> Assets;
    ActorProxy->Actor->GetReferencedContentObjects(Assets);

    // 创建资产拖拽操作，让 Slate 进入拖拽模式
    TSharedPtr<FAssetDragDropOp> DragDropOperation =
        FAssetDragDropOp::New(FAssetData(Assets[0], true));
    FSlateApplication::Get().ProcessDragEnterEvent(OwnerWindow, DragDropEvent);
}
```

**设置持久化**（`UActorPaletteSettings`）：

- 配置存储在 `EditorPerProjectUserSettings`（每项目、每用户）
- `RecentlyUsedList`：最近使用列表，上限可配置（默认 10，最大 25）
- `MostRecentLevelByTab`：每个 Tab 上次打开的关卡
- `FavoritesList`：收藏的关卡列表

### 快捷键

| 快捷键 | 功能 |
|---|---|
| G | 切换 Game View（游戏视图模式） |
| 右键拖拽 | 旋转相机（标准编辑器视口行为） |
| 左键拖拽 Actor | 发起资产拖拽操作 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `UnrealEd` | 编辑器框架（FEditorViewportClient 等） |
| `Slate` / `SlateCore` | UI 框架 |
| `ContentBrowser` | 资产选择器（Choose Level 弹出菜单中的资产浏览器） |
| `WorkspaceMenuStructure` | 编辑器 Tools 菜单注册 |
| `ToolMenus` | 菜单扩展 |
| `DeveloperSettings` | UDeveloperSettings 基类 |
| `InputCore` | 输入按键定义 |
| `Projects` | 插件路径查询 |
| `CoreUObject` / `Engine` | 引擎基础模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 提交说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 自动化代码维护工具批量添加，无功能变化 |
| 2025-06-10 | `bb3758b` | SEditorViewport::MakeViewportToolbar() is deprecated | 适配引擎 API 废弃，改为 `BuildViewportToolbar()` |
| 2024-11-15 | `a2c3875` | Cleanup of FSlateFontInfo constructor across the solution | 全局清理字体路径构造方式，无功能变化 |

### 维护评价

- **创建时间**：2020-09-01，已存在约 5.7 年
- **维护状态**：**不活跃** — 最近 3 次提交全部是编译修复和 API 适配，没有任何功能性更新
- **实验性标签**：`IsBetaVersion=true`，`EnabledByDefault=false`，从未毕业为正式插件
- **已知问题**（源码 TODO 注释）：
  - 拖拽完成后选择状态未清除
  - 只支持 Mesh 资产拖拽，不支持 Material 等其他资产类型
  - `RenameForPIE` 是临时 workaround
  - 相机位置不会持久化保存
  - 没有关卡自动刷新机制
- **推荐**：可用作关卡设计参考工具，但不建议在生产流程中深度依赖。作为 Epic 自身的实验性工具，代码质量不错，适合学习编辑器 Viewport 开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ActorPalette)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ActorPalette)：无独立测试文件
