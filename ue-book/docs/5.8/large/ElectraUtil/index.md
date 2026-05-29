# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | 媒体播放工具 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (RuntimeNoCommandlet), `ElectraSamples` (RuntimeNoCommandlet), `ElectraHTTPStream` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 是 Unreal Engine 中 Electra 媒体播放框架的核心基础组件集合。它提供了一套可重用的底层工具模块，用于构建高性能、跨平台的媒体播放功能，特别是针对流媒体场景。

这个插件解决了媒体播放中的几个关键问题：
- **跨平台抽象**：封装了不同平台（Windows、Mac、iOS、Android、Linux）的媒体解码和播放差异
- **流媒体支持**：提供完整的 HTTP 流媒体传输和缓冲管理机制
- **底层解码支持**：提供媒体样本的读取、解析和准备，供上层播放器使用
- **时间码处理**：精确的媒体时间码管理，包括子帧精度的处理

ElectraUtil 不是完整的播放器，而是 Electra 播放器框架的基础构建块。其他媒体播放插件（如 ElectraPlayer）依赖这些基础组件来实现完整的播放功能。

## 使用场景

- **开发自定义媒体播放器**：当你需要构建支持复杂媒体格式和流媒体协议的播放器时
- **流媒体应用开发**：需要处理 HLS、DASH 等自适应比特率流媒体协议
- **跨平台媒体应用**：应用需要在多个平台上提供一致的媒体播放体验
- **高性能媒体处理**：对媒体解码性能和内存管理有严格要求的场景
- **时间码精确同步**：需要精确时间码的应用，如视频编辑、特效合成等

## 蓝图用法

该插件主要提供底层 C++ API，没有公开的蓝图节点。所有功能通过 C++ 代码访问。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraBase.h"       // 基础功能
#include "ElectraSamples.h"    // 媒体样本处理
#include "ElectraHTTPStream.h" // HTTP 流媒体支持
```

### 基本用法

基于模块文档中的示例，以下是使用 ElectraUtil 的基本模式：

```cpp
// 包含必要的头文件
#include "ElectraBase.h"
#include "ElectraHTTPStream.h"

// 创建 HTTP 流媒体连接
class FMyMediaHandler
{
public:
    void InitializeStream()
    {
        // 创建 HTTP 流客户端（示例，具体 API 参见模块文档）
        TSharedPtr<FMediaStream, ESPMode::ThreadSafe> Stream = 
            FMediaStreamFactory::CreateStream(TEXT("https://example.com/media.m3u8"));
        
        if (Stream.IsValid())
        {
            // 设置流参数和回调
            Stream->SetBufferingParameters(/* ... */);
            Stream->SetProgressiveBufferingMode(false);
            
            // 开始流媒体加载
            Stream->Start();
        }
    }
};

// 媒体样本处理示例
void ProcessMediaSample()
{
    // 创建媒体样本
    TSharedPtr<FElectraMediaSample, ESPMode::ThreadSafe> Sample = 
        MakeShared<FElectraMediaSample>();
    
    // 配置样本信息
    FMediaSampleInfo SampleInfo;
    SampleInfo.Duration = FTimespan::FromSeconds(0.033); // 30fps
    SampleInfo.Timestamp = FTimespan::FromSeconds(1.5);
    
    Sample->SetSampleInfo(SampleInfo);
    Sample->SetSampleData(/* 样本数据指针 */);
    
    // 样本可以在解码管线中使用
    ProcessSampleInPipeline(Sample);
}
```

### 进阶用法

结合多个模块实现完整的媒体处理管线：

```cpp
#include "ElectraBase.h"
#include "ElectraSamples.h"
#include "ElectraHTTPStream.h"

class FAdvancedMediaPlayer
{
public:
    void BuildMediaPlayerPipeline()
    {
        // 1. 创建 HTTP 流媒体源
        TSharedPtr<FMediaStream> HttpStream = CreateHttpStream(MediaUrl);
        
        // 2. 创建样本解复用器
        TSharedPtr<FSampleDemuxer> Demuxer = MakeShared<FSampleDemuxer>();
        Demuxer->SetInputStream(HttpStream);
        
        // 3. 设置样本处理回调
        Demuxer->SetOnSampleReadyCallback([this](TSharedPtr<FElectraMediaSample> Sample)
        {
            OnMediaSampleReady(Sample);
        });
        
        // 4. 创建时间码管理器
        TSharedPtr<FTimecodeManager> TimecodeMgr = MakeShared<FTimecodeManager>();
        TimecodeMgr->Initialize(MediaFrameRate);
        
        // 5. 连接整个管线
        HttpStream->ConnectTo(Demuxer);
        Demuxer->ConnectTo(TimecodeMgr);
        
        // 启动播放管线
        HttpStream->Start();
    }
    
private:
    void OnMediaSampleReady(TSharedPtr<FElectraMediaSample> Sample)
    {
        // 精确处理时间码，包括子帧精度
        FTimecode SampleTimecode = 
            FTimecode::FromMPEGTime(Sample->GetTimecode(), bUseDropFrameTimecode);
        
        // 处理样本...
    }
};
```

## 模块依赖

从各个模块的 Build.cs 分析，使用 ElectraUtil 需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 媒体工具函数和数据结构 |
| `MediaAssets` | 媒体资产相关的数据类型 |
| `DirectX` | Windows 平台的 DirectX 支持（仅 ElectraSamples 模块） |
| `HTTP` | HTTP 网络请求支持（仅 ElectraHTTPStream 模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为服务器构建添加存根方法，防止链接错误 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复HDR归一化因子，解决媒体间亮度级别不正确的问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，使其更易于其他客户端使用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移到UE_LOGF |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复从MPEG定义创建时间码时的子帧精度损失问题 |

### 维护评价

**活跃维护**：ElectraUtil 插件处于活跃维护状态，最近 6 个月内有多次重要更新：
1. **最近更新**：2026年5月26日，增加了服务器构建的兼容性修复
2. **问题修复**：频繁修复HDR、时间码精度等关键功能问题
3. **技术更新**：正在现代化内部架构，提高可维护性
4. **平台兼容**：持续改进多平台支持

该插件是 Unreal Engine 媒体框架的核心组成部分，由 Epic Games 官方维护，适合作为构建媒体播放功能的基础设施。虽然默认未启用，但在需要媒体播放功能的项目中是推荐启用的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Media)（注意：测试可能在独立的测试目录中）