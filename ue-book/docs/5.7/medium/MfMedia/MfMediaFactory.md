# Media Foundation Media Player

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (Runtime), `MfMediaEditor` (Editor), `MfMediaFactory` (Runtime, Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia) | |

## 用途

基于微软 Media Foundation 框架（Windows 7+ / Xbox One）实现硬件加速的媒体播放能力。该插件允许在虚幻引擎中播放本地视频文件、网络流媒体以及摄像头/采集卡输入，提供低延迟、高兼容性的媒体回放方案。它是 UE 媒体框架（Media Framework）的原生后端之一，专门针对 Windows 平台优化。

## 使用场景

- 需要播放 MP4、WMV 等 Windows 原生格式视频的 UI/游戏内视频播放
- 需要利用硬件解码（DXVA）降低 CPU 占用的高清视频场景
- 集成摄像头或采集卡实时画面（通过 Media Foundation 的 Capture API）
- 作为媒体播放器资产（MediaPlayer）的后端，与 MediaTexture / MediaSound 组件配合使用

## 蓝图用法

本插件主要由 `MfMediaFactory` 模块作为“媒体工厂”自动注册到媒体框架，无需手动蓝图节点。蓝图层面仅需使用标准媒体框架节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建媒体播放器` (Create Media Player) | 创建媒体播放器资产，选择“MfMedia”作为播放器 | `UMediaPlayer` |
| `打开文件` (Open Source) | 指定源（文件路径/URL），MfMediaFactory 会按置信度自动选择 | `UMediaPlayer` |
| `播放/暂停` (Play/Pause) | 控制播放状态 | `UMediaPlayer` |
| `获取媒体纹理` (Get Media Texture) | 获取视频渲染目标纹理，用于 UI 或材质 | `UMediaTexture` |

### 使用示例

1. 创建 `MediaPlayer` 资产（蓝图类中新建变量类型为 MediaPlayer）。
2. 调用 `Open Source` 节点，将 `MediaSource` 设为文件路径（如 `file:///C:/video.mp4`）。
3. 创建 `MediaTexture` 资产，其 `MediaPlayer` 关联上述播放器。
4. 在材质中使用 `MediaTexture` 作为纹理，或直接拖入 UMG Image 的 Brush。

> 注意：需要在项目设置中启用插件（Plugins → Media Players → MfMedia）。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
// 工厂模块无需直接引用，MfMediaFactory 自动完成注册
```

### 基本用法

```cpp
// 通过媒体框架创建媒体播放器
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyClass::OnMediaOpened);

// 打开媒体源（文件路径）
FString FilePath = FPaths::ProjectContentDir() / TEXT("Videos/intro.mp4");
UMediaSource* MediaSource = UFileMediaSource::StaticClass()->GetDefaultObject<UFileMediaSource>();
MediaSource->FilePath = FilePath;

MediaPlayer->OpenSource(MediaSource);
```

*来源文件：* `Engine/Plugins/Media/MfMedia/Source/MfMediaEditor/Private/MfMediaEditorModule.cpp`（示例参考，实际项目代码）

### 进阶用法

通过 `IMediaPlayer` 接口获取更底层控制：

```cpp
// 获取当前活跃的媒体播放器
const TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MfPlayer = MediaPlayer->GetPlayer();
if (MfPlayer.IsValid())
{
    // 查询支持的媒体类型
    const FName PlatformName = TEXT("MfMedia");
    if (MfPlayer->GetPlayerName() == PlatformName)
    {
        // 获得原生 Media Foundation 会话（需包含 Windows 头）
        // IMfMediaPlayer* NativePlayer = static_cast<IMfMediaPlayer*>(MfPlayer.Get());
    }
}
```

*来源文件：* `Engine/Plugins/Media/MfMedia/Source/MfMedia/Private/Player/MfMediaPlayer.h`

## 模块依赖

本模块（`MfMediaFactory`）作为工厂模块，依赖 `Media` 框架，无需额外非标准依赖。

| 模块 | 用途 |
|---|---|
| `Media` | 媒体框架核心接口 |
| `MediaAssets` | 提供 MediaPlayer、MediaSource 等资产类 |
| `MediaUtils` | 媒体播放实用工具 |

> 项目使用方只需在 `.Build.cs` 中添加 `"MfMediaFactory"` 到 `PublicDependencyModuleNames` 即可，其余模块会自动加载。

## 维护状态

### 近期更新

- 2025-06-20 `642aa84c` 修复 PVS 静态分析警告
- 2025-02-18 `0ecd6846` 媒体：重写时间戳关联序列索引逻辑
- 2025-02-06 `81c434be` 媒体：新增 "MediaBufferingComplete" 事件
- 2024-12-18 `6ed576ac` [格式字符串安全检查] 禁止通过 %d 打印 TCHAR* 并修复所有出现
- 2024-05-06 `1d0682a5` 媒体：`CanPlayUrl()` 返回置信度值

### 维护评价

- **创建时间**：2024-05-06（约1年）
- **最近更新频率**：2025年6月有功能性修复，2025年初有事件新增与重构，维护活跃
- **活跃度**：仍在积极维护，有核心媒体框架的大幅改动时同步更新
- **已知问题**：仅支持 Windows 平台，Xbox One 声明但未广泛测试；低版本 Windows 可能需要额外运行时组件
- **推荐使用**：✅ 适合 Windows 原生媒体播放场景，性能优异，建议用于生产项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia)
- [官方论坛文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/AutomationTool/NotForDistribution/TestData/Media)