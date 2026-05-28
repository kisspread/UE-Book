# Actor Palette

> Allows creation of Actor Palettes based on existing levels to quickly select actors and drag them into the level editor

| 属性 | 值 |
|---|---|
| 中文名 | Actor 调色板 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorPalette` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ActorPalette) | |

## 用途

Actor Palette 是一个纯编辑器工具，解决"跨关卡复用 Actor 资产"的痛点。

在大型项目中，美术和设计师经常需要把一个关卡里的 Actor（如场景摆件、灯光配置、UI 元素等）复制到另一个关卡。标准做法是打开源关卡 → 选中 Actor → 复制 → 切换到目标关卡 → 粘贴，流程繁琐且容易出错。

Actor Palette 提供了一个**停靠式预览窗口**，直接在编辑器中以独立视口加载任意关卡，用户可以在该窗口中浏览 Actor，然后拖拽到当前正在编辑的关卡中。最多支持同时打开 **4 个** Actor Palette 标签页，并且会记住每个标签页上次打开的关卡、最近使用列表和收藏列表。

## 使用场景

- 你有多个关卡包含可复用的场景资产（摆件、灯光预设等），想快速拖拽到当前关卡
- 你想在一个小窗口中浏览某个"资产库关卡"的内容，而不用完整加载它
- 你需要同时参考多个关卡的 Actor 布局，频繁在它们之间切换
- 你想建立一个"收藏夹"，标记常用资产关卡以便快速访问

## 蓝图用法

此插件为纯 C++ 编辑器工具，不暴露 BlueprintCallable API。所有交互通过编辑器 UI 完成。

### 核心 UI 交互

| 交互 | 说明 |
|---|---|
| 打开 Palette 窗口 | 通过菜单或快捷键打开（最多 4 个标签页） |
| 切换游戏模式显示 | `ToggleGameView` 命令，切换视口的游戏模式渲染 |
| 重置摄像机视角 | `ResetCameraView` 命令，恢复默认观察角度 |
| 选择关卡 | 通过视口工具栏的关卡选择菜单加载不同关卡 |
| 收藏关卡 | 通过 `ToggleFavorite` 将关卡加入/移出收藏列表 |
| 拖拽 Actor | 从 Palette 视口直接拖拽 Actor 到当前关卡 |

## C++ 用法

### 头文件引入

```cpp
#include "ActorPaletteModule.h"
#include "ActorPaletteViewportClient.h"
#include "ActorPaletteSettings.h"
```

### 基本用法：加载关卡到 Palette 视口

`FActorPaletteViewportClient` 是核心类，负责在预览场景中流式加载关卡。

```cpp
// Source: ActorPaletteViewportClient.h

// 1. 获取 ActorPalette 视口客户端（通常通过模块获取 tab 实例）
TSharedPtr<FActorPaletteViewportClient> ViewportClient =
    MakeShared<FActorPaletteViewportClient>(/*TabIndex=*/0);

// 2. 将某个关卡作为 Actor 调色板打开
FAssetData SourceWorldAsset = ...; // 通过 AssetRegistry 查找关卡资产
ViewportClient->OpenWorldAsPalette(SourceWorldAsset);

// 3. 查询当前打开的关卡
FAssetData CurrentAsset = ViewportClient->GetCurrentWorldAssetData();

// 4. 重置观察视角
ViewportClient->ResetCameraView();
```

### 进阶用法：管理设置与收藏

`UActorPaletteSettings` 存储用户的使用历史和偏好，自动持久化到 `EditorPerProjectUserSettings`。

```cpp
// Source: ActorPaletteSettings.h

UActorPaletteSettings* Settings = GetMutableDefault<UActorPaletteSettings>();

// 查找关卡的设置索引
int32 EntryIndex = Settings->FindMapEntry(TEXT("/Game/Maps/MyPaletteLevel"));

// 标记为最近使用（会自动提升到最近列表顶部）
Settings->MarkAsRecentlyUsed(MapAsset, /*TabIndex=*/0);

// 切换收藏状态
Settings->ToggleFavorite(MapAsset);

// 访问最近使用列表
for (const FString& RecentMap : Settings->RecentlyUsedList)
{
    UE_LOG(LogTemp, Log, TEXT("Recent: %s"), *RecentMap);
}

// 访问收藏列表
for (const FString& FavMap : Settings->FavoritesList)
{
    UE_LOG(LogTemp, Log, TEXT("Favorite: %s"), *FavMap);
}

// 配置保留的最近关卡数量（0-25）
Settings->NumRecentLevelsToKeep = 15;
```

### 进阶用法：自定义 Palette 标签页

```cpp
// Source: ActorPaletteModule.h

// 模块管理最多 4 个标签页
// 每个标签页有独立的 TabID 和弱引用到 SActorPalette 实例
FActorPaletteModule* Module = FModuleManager::GetModulePtr<FActorPaletteModule>("ActorPalette");

// 通过命令触发新标签页创建
Module->PluginButtonClicked();
```

## Demo 示例

一个最小的自定义 Palette 视口客户端示例，展示如何在自己的编辑器工具中复用关卡流式加载逻辑：

```cpp
// MyPaletteTool.h
#pragma once

#include "CoreMinimal.h"
#include "ActorPaletteViewportClient.h"

class FMyPaletteTool
{
public:
    void Init(int32 TabIndex);
    void LoadLevel(const FAssetData& LevelAsset);
    void ResetView();

private:
    TSharedPtr<FActorPaletteViewportClient> ViewportClient;
};

// MyPaletteTool.cpp
#include "MyPaletteTool.h"

void FMyPaletteTool::Init(int32 TabIndex)
{
    ViewportClient = MakeShared<FActorPaletteViewportClient>(TabIndex);
}

void FMyPaletteTool::LoadLevel(const FAssetData& LevelAsset)
{
    if (ViewportClient.IsValid())
    {
        ViewportClient->OpenWorldAsPalette(LevelAsset);
    }
}

void FMyPaletteTool::ResetView()
{
    if (ViewportClient.IsValid())
    {
        ViewportClient->ResetCameraView();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelEditor` | 关卡编辑器集成，提供拖拽 Actor 目标 |
| `WorkspaceMenuStructure` | 工作区标签页菜单结构 |
| `Toolkits` | 编辑器工具集框架（标签页管理） |

> 无其他特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-18 | `aad3f91f` | PR #14135: Display ticked objects in ActorPalette viewport, when realtime toggle is enabled | 开启实时渲染时在 Palette 视口显示动态对象 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏，编译优化 |
| 2025-06-10 | `bb3758b4` | SEditorViewport::MakeViewportToolbar() is deprecated. | 适配已废弃的视口工具栏 API |
| 2024-11-15 | `a2c3875d` | Cleanup of FSlateFontInfo constructor across the solution that uses font paths. It will be deprecate | 全局清理字体构造函数用法 |
| 2023-11-17 | `73fb240e` | Remove unwanted ReloadTextureResources that clear cached for all textures and atlas. | 移除多余的纹理重载调用，避免清除缓存 |

### 维护评价

- **创建时间**：2020 年 9 月，约 5 年历史
- **标记状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，属于实验性插件
- **更新频率**：最近一次功能性更新在 2025 年 12 月（显示动态对象），但 2023-2025 期间的更新主要是编译适配和 API 弃用修复，而非功能增强
- **代码质量**：源码中有多处 `@TODO` 注释（如视口记忆、列表清理），说明功能尚未完全实现
- **推荐程度**：⚠️ **谨慎使用**。作为实验性 Beta 插件，功能基本可用但不够成熟，没有官方文档，长期维护依赖 Epic 内部需求。适合在原型阶段快速试用，不建议在生产项目中深度依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ActorPalette)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ActorPalette/Tests)：未发现测试目录