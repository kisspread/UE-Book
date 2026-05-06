# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、EXR处理窗口、自定义属性面板） |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia) | |

## 用途

Image Sequence Media Player（图像序列媒体播放器）用于在虚幻引擎中播放图像序列（如 EXR、PNG、JPEG 等格式的连续图片）作为视频媒体。它支持高性能的平铺（tiling）和多级渐进纹理（mipmap）预处理，特别适合处理超高清（8K+）的序列帧，可用于电影级渲染、虚拟制片、视效预览等场景。编辑器模块（ImgMediaEditor）提供了 EXR 序列的批量预处理工具（生成 tile 和 mip）、带宽监控面板以及缓存管理 UI。

## 使用场景

- 你需要在引擎中播放 8K 以上的 EXR 图像序列作为视频背景或材质序列 → 使用 Image Sequence Media Player 并启用 tiling/mipmap。
- 你希望将长时间序列的 EXR 文件预先处理成平铺+mip 格式以节省内存和加载时间 → 使用编辑器中的 “Process EXR” 工具。
- 你需要实时监控图像序列播放的带宽占用 → 使用带宽监控面板（SImgMediaBandwidth）。
- 你希望方便地在内容浏览器中创建并配置图像序列媒体源 → 使用工厂和自定义细节面板。

## 蓝图用法

> 本插件核心运行时节点位于 `ImgMedia` 模块，通过标准媒体框架（`MediaPlayer`、`MediaTexture`、`MediaSource` 等）暴露给蓝图。  
> 编辑器模块（ImgMediaEditor）不直接提供蓝图可调用函数，但提供了资产创建和配置的编辑器支持。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `获取图像序列媒体源`（创建/选择） | 在内容浏览器中右键创建 `ImgMediaSource` 资产 | `UImgMediaSourceFactoryNew` |
| `打开媒体源` | 使用 `UMediaPlayer::OpenSource` 传入 `ImgMediaSource` 即可播放 | `UMediaPlayer`（引擎原生） |
| `绑定媒体纹理` | 使用 `UMediaTexture` 关联 `MediaPlayer` 并赋值给材质 | `UMediaTexture`（引擎原生） |

### 使用示例（蓝图描述）

1. 在内容浏览器中创建 `Media Player` 和 `Media Texture` 资产。
2. 将目标图像序列文件夹（包含连续图片）拖入内容浏览器，选择创建 `ImgMediaSource`。
3. 打开关卡蓝图，拖出 `MediaPlayer` 节点，调用 `Open Source`，选择上一步创建的 `ImgMediaSource`。
4. 将 `MediaPlayer` 连接到 `MediaTexture` 的 `Set Media Player` 节点。
5. 将 `MediaTexture` 拖入材质蓝图作为纹理采样，应用到任意网格体。

## C++ 用法

### 头文件引入

```cpp
#include "ImgMediaSource.h"           // 图像序列媒体源
#include "MediaPlayer.h"              // 媒体播放器
#include "MediaTexture.h"             // 媒体纹理
// ImgMediaEditor 模块工具（如需编辑器功能）
#include "ImgMediaProcessEXROptions.h"
#include "SImgMediaProcessEXR.h"
```

### 基本用法

**创建并播放图像序列（运行时）**
```cpp
// 在任意 Actor 或组件中
UMediaPlayer* MediaPlayer = CreateObject<UMediaPlayer>();
UMediaTexture* MediaTexture = CreateObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);

UImgMediaSource* Source = NewObject<UImgMediaSource>();
Source->SetSequencePath(TEXT("/Game/MySequence/")); // 设置序列所在目录

MediaPlayer->OpenSource(Source);
// 将 MediaTexture 赋值给材质实例
```
*来源：Engine/Plugins/Media/ImgMedia/Source/ImgMedia/Private/Player/ImgMediaPlayer.cpp 及常见用法*

**编辑器：打开 EXR 处理窗口**
```cpp
// 需要创建 SImgMediaProcessEXR 并插入到某个窗口或面板
TSharedRef<SWindow> Window = SNew(SWindow)
    .Title(FText::FromString("Process EXR Sequence"))
    .Content()
    [
        SNew(SImgMediaProcessEXR)
    ];
FSlateApplication::Get().AddWindow(Window);
// 设置输入路径
SImgMediaProcessEXR* Widget = (SImgMediaProcessEXR*)&Window->GetContent();
Widget->SetInputPath(TEXT("/Game/MySequence/"));
```
*来源：Engine/Plugins/Media/ImgMedia/Source/ImgMediaEditor/Private/Widgets/SImgMediaProcessEXR.h*

### 进阶用法

**自定义属性面板（FImgMediaSourceCustomization）**  
在 `ImgMediaSource` 的细节面板中，会显示序列路径拾取器、代理目录列表、无效路径警告图标等。该自定义由 `FImgMediaSourceCustomization` 实现，自动注册。
```cpp
// 如果您需要在自己的细节面板中复用路径拾取逻辑：
FString Path = FImgMediaSourceCustomization::GetSequencePathFromChildProperty(SomePropertyHandle);
```
*来源：Engine/Plugins/Media/ImgMedia/Source/ImgMediaEditor/Private/Customizations/ImgMediaSourceCustomization.h*

**通过 IImgMediaEditorModule 获取媒体播放器列表**
```cpp
IImgMediaEditorModule* Module = FModuleManager::GetModulePtr<IImgMediaEditorModule>("ImgMediaEditor");
if (Module)
{
    const TArray<TWeakPtr<FImgMediaPlayer>>& Players = Module->GetMediaPlayers();
    // 遍历播放器，可在带宽面板等中显示信息
}
```
*来源：Engine/Plugins/Media/ImgMedia/Source/ImgMediaEditor/Private/ImgMediaEditorModule.h*

## Demo 示例

以下是一个完整的编辑器模块示例，注册一个菜单项打开 EXR 处理窗口。

**ImgMediaEditorDemoCommands.h**
```cpp
#pragma once
#include "Framework/Commands/Commands.h"

class FImgMediaEditorDemoCommands : public TCommands<FImgMediaEditorDemoCommands>
{
public:
    FImgMediaEditorDemoCommands()
        : TCommands(TEXT("ImgMediaEditorDemo"), NSLOCTEXT("Contexts", "ImgMediaEditorDemo", "ImgMedia Editor Demo"), NAME_None, FEditorStyle::GetStyleSetName())
    {}

    virtual void RegisterCommands() override
    {
        UI_COMMAND(OpenProcessEXR, "Process EXR...", "Open the EXR processing tool", EUserInterfaceActionType::Button, FInputGesture());
    }

    TSharedPtr<FUICommandInfo> OpenProcessEXR;
};
```

**ImgMediaEditorDemo.cpp**
```cpp
#include "ImgMediaEditorDemoCommands.h"
#include "ImgMediaProcessEXROptions.h"
#include "Widgets/SImgMediaProcessEXR.h"
#include "LevelEditor.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "Widgets/Docking/SDockTab.h"

static const FName ProcessEXRTabName("ProcessEXR");

void OpenProcessEXRTab(FSpawnTabArgs SpawnArgs)
{
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            SNew(SImgMediaProcessEXR)
        ];
}

class FImgMediaEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        FImgMediaEditorDemoCommands::Register();

        PluginCommands = MakeShareable(new FUICommandList);
        PluginCommands->MapAction(
            FImgMediaEditorDemoCommands::Get().OpenProcessEXR,
            FExecuteAction::CreateRaw(this, &FImgMediaEditorDemoModule::OpenProcessEXR));

        FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
        TSharedPtr<FExtender> MenuExtender = MakeShareable(new FExtender);
        MenuExtender->AddMenuExtension(
            "WindowLayout",
            EExtensionHook::After,
            PluginCommands,
            FMenuExtensionDelegate::CreateRaw(this, &FImgMediaEditorDemoModule::AddMenuEntry));
        LevelEditorModule.GetMenuExtensibilityManager()->AddExtender(MenuExtender);

        // 注册 Tab 生成器
        FGlobalTabmanager::Get()->RegisterNomadTabSpawner(ProcessEXRTabName, FOnSpawnTab::CreateStatic(&OpenProcessEXRTab))
            .SetDisplayName(NSLOCTEXT("ImgMediaEditorDemo", "ProcessEXR", "Process EXR"));
    }

    virtual void ShutdownModule() override
    {
        FImgMediaEditorDemoCommands::Unregister();
        FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(ProcessEXRTabName);
    }

private:
    void AddMenuEntry(FMenuBuilder& MenuBuilder)
    {
        MenuBuilder.AddMenuEntry(FImgMediaEditorDemoCommands::Get().OpenProcessEXR);
    }

    void OpenProcessEXR()
    {
        FGlobalTabmanager::Get()->InvokeTab(ProcessEXRTabName);
    }

    TSharedPtr<FUICommandList> PluginCommands;
};

IMPLEMENT_MODULE(FImgMediaEditorDemoModule, ImgMediaEditorDemo)
```

## 模块依赖

**使用本插件时，您的模块需要添加以下依赖：**

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaTexture`、`UMediaSource` 等媒体框架资产 |
| `MediaUtils` | 媒体播放器底层工具 |
| `MediaIOCore` | 媒体 IO 核心，提供时间管理等 |

> 子模块 `OpenExrWrapper` 和 `ExrReaderGpu` 为内部实现，通常不需要直接依赖。  
> 编辑器模块 `ImgMediaEditor` 依赖 `UnrealEd`、`PropertyEditor`、`EditorWidgets` 等编辑器基础设施（已省略常见依赖）。

**完整依赖列表（来自各 Build.cs）**：

| 模块 | Public 依赖 | Private 依赖 |
|---|---|---|
| `ExrReaderGpu` | `OpenExrWrapper` | (无额外) |
| `ImgMedia` | `MediaAssets`, `MediaUtils`, `MediaIOCore`, `OpenExrWrapper`, `ExrReaderGpu` | `UnrealEd` |
| `ImgMediaEditor` | `OpenExrWrapper`, `UnrealEd` | `PropertyEditor`, `ImageWriteQueue` 等 |
| `ImgMediaEngine` | 无特殊 | 无特殊 |
| `ImgMediaFactory` | `MediaAssets` | 无特殊 |
| `OpenExrWrapper` | 第三方 OpenEXR 库 | 无 |

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-10-17 | f81b388d | [ImgMedia] 修复由未保护的大帧间隔导致的 OOM 崩溃 |
| 2025-10-10 | ebdf8ce6 | [ImgMedia] 处理擦除（scrubbing）时的全局缓存帧驱逐问题 |
| 2025-09-29 | f131b1dc | [ImgMedia] 修复在异步加载中创建非安全游戏 tick 对象的问题 |
| 2025-08-21 | 2c158c4d | 更改 `GetUsedTextures MaterialInterface` 参数为 `TOptional` |
| 2025-08-15 | ae8bb436 | ImgMedia: 根据序列帧率设置帧持续时间而非使用全局值 |

### 维护评价

- **创建时间**：2025-08-15（约 2 个月前）
- **最近更新频率**：最近一个月内有多次功能性修复和优化，提交活跃。
- **活跃度**：**活跃维护中**，目前没有发现废弃或停滞迹象。
- **已知问题**：commit 中提及了 OOM 崩溃和 scrubbing 缓存问题，均已修复。
- **推荐使用**：✅ 强烈推荐。此插件性能经过优化（GPU 读取、平铺渲染），且持续获得 Epic 的维护。适用于需要高分辨率图像序列播放的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia)
- [官方文档（论坛帖）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia/Source/ImgMediaEditor/Private)（编辑器模块源码，内部包含部分单元测试逻辑）