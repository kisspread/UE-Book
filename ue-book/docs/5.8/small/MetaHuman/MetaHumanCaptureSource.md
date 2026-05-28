# MetaHuman Capture Source

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 捕获源模块 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanCaptureSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-10-05 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureSource) | |

> ⚠️ **该模块已废弃（UE 5.7）**。功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块。本文档记录的历史 API 仅作参考，新项目不应使用。

## 用途

该模块是 MetaHuman Animator 管线中的**素材捕获与导入**层，负责将演员面部表演的原始素材（视频、深度图、音频）从物理设备或归档文件导入到 Unreal Engine 中，生成可供 MetaHuman Performance 资产使用的 Take 数据。

具体解决以下问题：
- **设备连接管理**：通过 LiveLink Face 应用与 iOS 设备建立网络连接，获取设备上录制的 Take 列表
- **多格式素材解析**：支持解析 LiveLink Face 归档（.mhaical 元数据）、HMC（头戴式相机）归档、立体重建系统等多种捕获格式的原始数据
- **数据转换管线**：将 MOV 视频转为图像序列（EXR）、提取音频为 WAV、解压/压缩深度数据、同步视频与深度帧
- **资产创建**：在 UE Content Browser 中创建 `UImgMediaSource`（图像序列）、`USoundWave`（音频）、`UCameraCalibration`（相机标定）等资产
- **事件系统**：当 Take 列表变化、连接状态改变、录制开始/结束时通知上层系统

## 使用场景

- 你使用 iPhone 上的 LiveLink Face 应用录制了演员面部表演 → 需要将录制素材导入 UE 中
- 你有 HMC（头戴式多相机）录制的立体素材归档 → 需要解析元数据、生成深度图、创建资产
- 你在构建 MetaHuman 动画管线，需要从捕获源批量导入多条 Take
- 你使用 MetaHuman Performance 资产驱动面部动画 → 需要先通过此模块获取素材数据

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanStartup` | 检查是否可以启动捕获源 | `UMetaHumanCaptureSourceSync` |
| `CanIngestTakes` | 检查是否可以导入 Take | `UMetaHumanCaptureSourceSync` |
| `CanCancel` | 检查是否可以取消当前操作 | `UMetaHumanCaptureSourceSync` |
| `Startup` | 启动捕获源，连接设备或扫描归档目录 | `UMetaHumanCaptureSourceSync` |
| `Refresh` | 刷新可用 Take 列表，返回 Take 信息数组 | `UMetaHumanCaptureSourceSync` |
| `SetTargetPath` | 设置素材导入的目标目录和资产路径 | `UMetaHumanCaptureSourceSync` |
| `Shutdown` | 关闭捕获源，释放连接和资源 | `UMetaHumanCaptureSourceSync` |
| `IsProcessing` | 检查当前是否正在处理（导入）素材 | `UMetaHumanCaptureSourceSync` |
| `IsCancelling` | 检查是否正在取消处理 | `UMetaHumanCaptureSourceSync` |
| `CancelProcessing` | 取消指定 Take 的处理 | `UMetaHumanCaptureSourceSync` |
| `GetNumTakes` | 获取可用 Take 总数 | `UMetaHumanCaptureSourceSync` |
| `GetTakeIds` | 获取所有 Take 的 ID 列表 | `UMetaHumanCaptureSourceSync` |
| `GetTakeInfo` | 获取指定 Take 的详细信息 | `UMetaHumanCaptureSourceSync` |
| `GetTakes` | 获取指定 Take 的完整数据（视频、深度、音频） | `UMetaHumanCaptureSourceSync` |

### 使用示例（蓝图描述）

**从 LiveLink Face 设备导入素材：**

1. 创建 `MetaHumanCaptureSourceSync` 对象
2. 设置 `CaptureSourceType` 为 `LiveLinkFaceConnection`，配置 `DeviceIpAddress` 和 `DeviceControlPort`
3. 调用 `Startup` 连接设备
4. 调用 `Refresh` 获取可用 Take 列表
5. 调用 `SetTargetPath` 设置导入目标目录
6. 调用 `GetTakes` 传入要导入的 Take ID 数组，开始素材导入
7. 在 Tick 中轮询 `IsProcessing` 检查导入进度
8. 导入完成后调用 `Shutdown` 断开连接

**从本地归档导入素材：**

1. 创建 `MetaHumanCaptureSourceSync` 对象
2. 设置 `CaptureSourceType` 为 `LiveLinkFaceArchives` 或 `HMCArchives`
3. 设置 `StoragePath` 为归档文件所在目录
4. 调用 `Startup` → `Refresh` → `SetTargetPath` → `GetTakes`

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCaptureSource.h"
#include "MetaHumanCaptureSourceSync.h"
#include "MetaHumanCaptureIngester.h"
#include "MetaHumanTakeData.h"
```

### 基本用法

使用同步接口从 LiveLink Face 归档导入 Take：

```cpp
// 来源: Public/MetaHumanCaptureSourceSync.h

// 创建同步捕获源
UMetaHumanCaptureSourceSync* CaptureSource = NewObject<UMetaHumanCaptureSourceSync>();
CaptureSource->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceArchives;
CaptureSource->StoragePath.Path = TEXT("/path/to/your/archives");

// 检查并启动
if (CaptureSource->CanStartup())
{
    CaptureSource->Startup();
    
    // 刷新 Take 列表
    TArray<FMetaHumanTakeInfo> Takes = CaptureSource->Refresh();
    
    // 设置导入目标路径
    CaptureSource->SetTargetPath(TEXT("/Game/Captures/"), TEXT("/Game/Captures/"));
    
    // 获取所有 Take ID
    TArray<int32> TakeIds = CaptureSource->GetTakeIds();
    
    // 开始导入
    if (!TakeIds.IsEmpty())
    {
        CaptureSource->GetTakes(TakeIds);
    }
}
```

### 进阶用法

使用异步 `FIngester` 接口，支持回调和进度监控：

```cpp
// 来源: Public/MetaHumanCaptureIngester.h

// 构建 Ingester 参数
UE::MetaHuman::FIngesterParams Params(
    EMetaHumanCaptureSourceType::LiveLinkFaceConnection,  // 连接类型
    FDirectoryPath{},                                      // 存储路径（连接模式下不需要）
    FDeviceAddress{TEXT("192.168.1.100")},                // 设备 IP
    14785,                                                 // 控制端口
    true,                                                  // 压缩深度文件
    true,                                                  // 拷贝图片到项目
    10.0f,                                                 // 最小深度距离(cm)
    25.0f,                                                 // 最大深度距离(cm)
    EMetaHumanCaptureDepthPrecisionType::Eightieth,        // 深度精度
    EMetaHumanCaptureDepthResolutionType::Full             // 深度分辨率
);

// 创建 Ingester
UE::MetaHuman::FIngester Ingester(Params);

// 监听 Take 完成事件
Ingester.OnGetTakesFinishedDelegate.AddLambda(
    [](const TArray<FMetaHumanTake>& InTakes)
    {
        for (const FMetaHumanTake& Take : InTakes)
        {
            UE_LOG(LogTemp, Log, TEXT("Take %d imported with %d views"),
                Take.TakeId, Take.Views.Num());
        }
    }
);

// 异步启动
Ingester.Startup(ETakeIngestMode::Async);

// 刷新 Take 列表
Ingester.Refresh(UE::MetaHuman::FIngester::FRefreshCallback::CreateLambda(
    [&Ingester](FMetaHumanCaptureVoidResult InResult)
    {
        if (InResult.bIsValid)
        {
            TArray<TakeId> TakeIds = Ingester.GetTakeIds();
            Ingester.GetTakes(TakeIds, 
                UE::MetaHuman::FIngester::FGetTakesCallbackPerTake());
        }
    }
));

// 查询处理进度
TOptional<float> Progress = Ingester.GetProcessingProgress(TakeId);
if (Progress.IsSet())
{
    UE_LOG(LogTemp, Log, TEXT("Progress: %.0f%%"), Progress.GetValue() * 100.0f);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanPipeline` | MetaHuman 数据处理管线，用于 Take 数据的转换流水线 |
| `MetaHumanCaptureProtocolStack` | LiveLink Face 通信协议栈，处理与 iOS 设备的网络通信 |
| `MetaHumanCaptureUtils` | 捕获工具函数库，提供通用的捕获数据处理工具 |
| `MediaUtils` | 媒体工具，用于视频/音频文件的读写 |
| `ImageWriteQueue` | 图像写入队列，用于异步写入深度图 EXR 序列 |
| `ImageWrapper` | 图像格式封装，用于 EXR/PNG 等格式的编解码 |
| `MediaAssets` | 媒体资产类型（`UImgMediaSource`、`USoundWave` 等） |

## 维护状态

### 近期更新

> ⚠️ 以下 git log 来自 MetaHumanAnimator 插件根目录，反映整个插件的更新情况，非此模块单独的更新。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**⚠️ 该模块已废弃。**

- **废弃时间**：UE 5.7 版本标记为 `UE_DEPRECATED(5.7, ...)`
- **功能迁移**：所有功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块
- **代码状态**：源码中大量类型、类、枚举均带有 `Deprecated` 元数据标记，编译时会产生废弃警告
- **推荐**：**不推荐在新项目中使用**。应使用新的 `CaptureManager/CaptureManagerDevices` 模块替代
- MetaHumanAnimator 插件整体仍在活跃维护（最近更新 2026-05-22），但维护重点已转向身体追踪等新功能和 Sequencer 集成

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureSource)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman/)
- [迁移目标模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/CaptureManager/CaptureManagerDevices)