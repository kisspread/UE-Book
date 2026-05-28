# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产模板、编辑器定制） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia) | |

## 用途

AjaMedia 插件为 Unreal Engine 提供与 **AJA 专业采集卡**（如 Corvid、Kona 系列）的深度集成，实现 SDI/HDMI 等专业视频信号的实时输入和输出。

该插件解决的核心问题是：**在虚拟制片、广播和实时合成场景中，需要将外部摄像机信号通过 AJA 硬件接入 Unreal Engine，或从 Unreal Engine 向 AJA 硬件输出合成画面**。

它基于 UE 的 Media Framework 扩展而来，利用 MediaIOCore 提供统一的媒体 I/O 抽象，与 BlackmagicMedia 等插件架构一致。插件仅支持 Win64 平台，且默认禁用（`EnabledByDefault=false`），需要在项目设置中手动启用。

### 模块职责

| 模块 | 职责 |
|---|---|
| `AjaCore` | AJA 硬件低层 API 封装，设备枚举、信号配置 |
| `AjaMedia` | Media Framework 集成，MediaPlayer、MediaSource、MediaTexture 实现 |
| `AjaMediaEditor` | 编辑器资产定义、资产工厂、属性自定义面板 |
| `AjaMediaFactory` | MediaFactory 集成，为 MediaFramework 提供 AJA 播放器创建能力 |
| `AjaMediaOutput` | 媒体输出功能，将 UE 画面实时输出到 AJA 硬件 |

## 使用场景

- **虚拟制片（Virtual Production）** — 将电影摄影机的 SDI 信号通过 AJA 采集卡接入 UE，实现实时合成和 LED 墙显示
- **广播图文** — 在演播室环境中，将 UE 生成的实时图文叠加到 AJA 视频流上
- **现场活动** — 使用 AJA 硬件从 UE 输出合成画面到现场大屏或导播台
- **多路输入/输出** — 同时管理多张 AJA 卡的多个输入输出通道
- **时间码同步** — 通过 AJA 硬件时间码实现 UE 与外部设备的帧精确同步

## 蓝图用法

> ⚠️ 该插件的蓝图 API 主要通过 Media Framework 标准接口暴露（`UMediaPlayer`、`UMediaSource`、`UMediaOutput`）。AJA 特定的类继承自这些基类，可在蓝图中以相同方式使用。

### 核心资产类型

| 资产类型 | 说明 |
|---|---|
| `UAjaMediaSource` | AJA 媒体源，配置输入通道、视频格式、帧率等参数 |
| `UAjaMediaOutput` | AJA 媒体输出，配置输出通道和视频格式 |
| `UMediaPlayer` | 标准媒体播放器，通过 MediaFactory 自动选择 AJA 播放器 |
| `UMediaTexture` | 将 AJA 输入视频渲染为纹理 |

### 创建和使用步骤（蓝图描述）

1. **创建 Media Source**：在内容浏览器中右键 → Media → AJA Media Source（在 "Media Sources + Outputs" 分类下）
2. **配置输入参数**：在源资产中选择 AJA 设备、输入连接器（SDI 1/2 等）、视频格式（1080p60 等）
3. **创建 Media Player**：右键 → Media → Media Player，打开后自动使用 AJA 播放器
4. **打开源**：蓝图中调用 `MediaPlayer->Open(Source)`
5. **创建 Media Texture**：右键 → Media → Media Texture，关联到 Media Player
6. **应用材质**：将 Media Texture 作为纹理采样器赋给材质，应用到场景中的网格体或 UI 上
7. **输出画面**：创建 AJA Media Output 资产，配置输出通道，使用 MediaOutput 节点将画面输出

## C++ 用法

### 头文件引入

```cpp
#include "AjaMediaSource.h"     // AJA 媒体源
#include "AjaMediaOutput.h"     // AJA 媒体输出
#include "MediaPlayer.h"        // 标准媒体播放器
#include "MediaTexture.h"       // 媒体纹理
```

### 基本用法 — 通过 C++ 打开 AJA 输入源

```cpp
// 创建 AJA Media Source
UAjaMediaSource* AjaSource = NewObject<UAjaMediaSource>();
AjaSource->SetDeviceIdentifier(/* 设备配置 */);
// 配置完成后用 MediaPlayer 打开
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->OpenSource(AjaSource);
```

> ⚠️ 由于未提供完整的 AjaMedia 模块头文件，以上为基于 Media Framework 基类的推断用法。实际 AJA 特定 API 需参考引擎源码。

### MediaIOCore 集成模式

AJA 插件通过 MediaIOCore 抽象层与其他采集卡插件（Blackmagic 等）共享统一的配置结构：

```cpp
// AJA 使用 MediaIOConfiguration 结构进行设备配置
// FMediaIOConfiguration 包含：
// - DeviceConfiguration（设备选择）
// - MediaConfiguration（视频格式、帧率）
// - bAutoDetect（自动检测信号格式）
```

### 时间码引用自定义

```cpp
// AjaMediaTimecodeReferenceCustomization 提供编辑器中的时间码配置 UI
// 继承自 FMediaIOCustomizationBase，提供设备选择和配置排列
FAjaMediaTimecodeReference SelectedConfiguration;
// 在编辑器中通过自定义属性面板选择时间码源
```

## Demo 示例

### 最小示例 — 创建 AJA Media Source 并打开

```cpp
// AjaDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "AjaDemoActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UAjaMediaSource;

UCLASS()
class AAjaDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AAjaDemoActor();

    UPROPERTY(EditAnywhere, Category = "AJA")
    UAjaMediaSource* AjaSource;

    UPROPERTY(VisibleAnywhere, Category = "AJA")
    UMediaPlayer* AjaPlayer;

    UPROPERTY(VisibleAnywhere, Category = "AJA")
    UMediaTexture* AjaTexture;

    UFUNCTION(BlueprintCallable, Category = "AJA")
    bool OpenAjaInput();

    UFUNCTION(BlueprintCallable, Category = "AJA")
    void CloseAjaInput();

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* DisplayMesh;
};
```

```cpp
// AjaDemoActor.cpp
#include "AjaDemoActor.h"
#include "AjaMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

AAjaDemoActor::AAjaDemoActor()
{
    DisplayMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DisplayMesh"));
    RootComponent = DisplayMesh;

    AjaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("AjaPlayer"));
    AjaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("AjaTexture"));
    AjaTexture->SetMediaPlayer(AjaPlayer);
}

bool AAjaDemoActor::OpenAjaInput()
{
    if (!AjaSource || !AjaPlayer)
    {
        return false;
    }

    bool bOpened = AjaPlayer->OpenSource(AjaSource);
    if (bOpened)
    {
        // 将 Media Texture 应用到动态材质实例
        UMaterialInstanceDynamic* DynMat = DisplayMesh->CreateDynamicMaterialInstance(0);
        if (DynMat)
        {
            DynMat->SetTextureParameterValue(TEXT("VideoTexture"), AjaTexture);
        }
    }
    return bOpened;
}

void AAjaDemoActor::CloseAjaInput()
{
    if (AjaPlayer)
    {
        AjaPlayer->Close();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaUtils` | Media Framework 基础工具 |
| `MediaAssets` | UMediaPlayer、UMediaTexture 等资产类 |
| `MediaIOCore` | 媒体 I/O 抽象层，AJA 和 Blackmagic 共享的设备配置框架 |
| `Media` | Media Framework 核心模块 |
| `AjaCore` | AJA SDK 底层封装（插件内部依赖） |

> AJA SDK 二进制文件（头文件和库文件）随插件分发，位于插件目录的 ThirdParty 或类似路径下，仅支持 Win64 平台。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 自动模式下为 Blackmagic 和 AJA 卡填充媒体配置 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多个媒体播放器和采集卡添加引擎分析信息 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制片资产分类并迁移资产 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 为具体 MediaSource 和 MediaOutput 子类补充 UAssetDefinition 注册 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**活跃维护中。** AjaMedia 插件自 2018 年创建以来持续维护，近期（2026 年 5 月）仍有功能性更新。从 commit 记录看：

- ✅ 最近 1 个月内有实质性功能更新（MediaIO 配置自动填充、分析信息、资产定义补充）
- ✅ 与 BlackmagicMedia 插件共同维护，保持架构一致性
- ✅ 受益于虚拟制片工作流的持续投入
- ⚠️ 默认禁用（`EnabledByDefault=false`），需手动在项目设置中启用
- ⚠️ 仅支持 Win64 平台，这是 AJA SDK 的平台限制
- ⚠️ 需要 AJA 硬件采集卡才能实际使用

**推荐使用场景**：项目中已有 AJA 采集卡硬件且需要 SDI/HDMI 专业视频 I/O 的虚拟制片或广播项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia)
- [官方文档 — Media Framework](https://docs.unrealengine.com/en-US/InteractiveExperiences/VideoPlaybackAndMediaMediaFramework/)（通用媒体框架文档，AJA 专用文档较少）
- [相关插件 — BlackmagicMedia](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)（架构相似的竞品采集卡插件）