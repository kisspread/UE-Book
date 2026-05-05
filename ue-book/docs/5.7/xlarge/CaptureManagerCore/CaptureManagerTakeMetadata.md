# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产） |
| 模块 | `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是 Epic 虚拟制片工具链中 **Capture Manager** 系统的核心基础层。它本身不是一个独立可用的功能插件，而是为两个上层插件提供共享基础设施：

- **Capture Manager App** — 用于连接外部捕获设备（如 iPhone、摄像机）并控制拍摄流程
- **Capture Manager Editor** — 在 UE 编辑器内管理捕获数据的导入、浏览和处理

该插件解决的核心问题是：将拍摄（Capture）流程中通用的协议通信、数据格式、元数据管理、UI 样式等抽象为独立模块，避免 App 和 Editor 两个插件之间的代码重复。

### 模块职责概览

| 模块 | 职责 |
|---|---|
| **CaptureManagerStyle** | UI 样式定义（图标、颜色、字体等），供编辑器 UI 使用 |
| **CaptureManagerTakeMetadata** | Take（一次拍摄）的元数据结构定义，包括设备信息、缩略图、Schema 版本管理 |
| **CaptureProtocolStack** | 与捕获设备通信的协议栈实现（网络消息收发、会话管理） |
| **CaptureUtils** | 通用工具函数（文件操作、路径处理等） |
| **DataIngestCore** | 数据摄取核心逻辑（从设备接收数据并写入本地） |
| **LiveLinkHubCaptureMessaging** | 与 LiveLink Hub 之间的消息通信协议 |

## 使用场景

- 你正在开发虚拟制片流程，需要从 iPhone/摄像机等设备捕获表演数据 → 上层插件 **Capture Manager App** 依赖本插件
- 你需要在编辑器中浏览、管理拍摄 Take 数据 → 上层插件 **Capture Manager Editor** 依赖本插件
- 你需要自定义捕获设备通信协议 → 参考 **CaptureProtocolStack** 模块
- 你需要解析或生成 Take 元数据文件 → 使用 **CaptureManagerTakeMetadata** 模块

> ⚠️ 本插件 `EnabledByDefault=false`，通常不需要手动启用——它会被 Capture Manager App/Editor 自动依赖加载。

---

# CaptureManagerTakeMetadata 模块

> Take 元数据的数据结构定义模块，管理拍摄记录的设备信息、缩略图和 Schema 版本。

## 用途

CaptureManagerTakeMetadata 定义了 Capture Manager 系统中 **Take（一次拍摄记录）** 的核心数据结构。每次使用捕获设备完成一次拍摄后，系统会生成一个 Take 元数据文件（`.take` 扩展名），记录：

- 拍摄使用的设备信息（平台、序列号、镜头参数等）
- 拍摄的缩略图（支持从文件路径、压缩数据、原始像素数据多种方式构造）
- Schema 版本（用于向前/向后兼容性管理）

该模块是纯数据结构定义，不包含业务逻辑，被 DataIngestCore（写入）和 Capture Manager Editor（读取/展示）共同依赖。

## 蓝图用法

本模块为纯 C++ 数据结构模块，**不暴露蓝图 API**。所有类均为非 UObject 的 C++ 结构体/类，供其他模块在 C++ 层使用。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerTakeMetadata.h"
```

### 基本用法 — 缩略图管理

`FTakeThumbnailData` 支持从多种数据源构造缩略图：

```cpp
#include "CaptureManagerTakeMetadata.h"

// 方式 1：从文件路径加载
FTakeThumbnailData ThumbnailFromFile(TEXT("/path/to/thumbnail.png"));

// 方式 2：从压缩的图像数据构造
TArray<uint8> CompressedData = LoadCompressedImage();
FTakeThumbnailData ThumbnailFromData(MoveTemp(CompressedData));

// 方式 3：从原始像素数据构造
TArray<FColor> RawPixels;
uint32 Width = 256;
uint32 Height = 256;
FTakeThumbnailData ThumbnailFromRaw(MoveTemp(RawPixels), Width, Height, ERawImageFormat::BGRA8);

// 方式 4：使用赋值运算符
FTakeThumbnailData Thumbnail;
Thumbnail = TEXT("/path/to/thumbnail.png");           // 从路径
Thumbnail = MoveTemp(CompressedData);                  // 从压缩数据

// 访问缩略图数据
TOptional<TArray<uint8>> Data = Thumbnail.GetThumbnailData();   // 获取压缩数据
TOptional<FString> Path = Thumbnail.GetThumbnailPath();          // 获取文件路径
TOptional<FTakeThumbnailData::FRawImage> Raw = Thumbnail.GetRawImage(); // 获取原始图像
```

> 来源：`CaptureManagerTakeMetadata/Public/CaptureManagerTakeMetadata.h`

### 基本用法 — Take 元数据

```cpp
#include "CaptureManagerTakeMetadata.h"

// Take 元数据文件扩展名
FString Extension = FTakeMetadata::FileExtension;  // ".take"

// Schema 版本比较
FTakeMetadata::FSchemaVersion V1{1, 0};
FTakeMetadata::FSchemaVersion V2{2, 3};
bool bIsOlder = V1 < V2;  // true
bool bIsEqual = V1 == V2; // false

// 设备信息
FTakeMetadata::FDevice Device;
Device.FPlatform Platform;
Platform.Name = TEXT("iPhone");
Platform.Version = TEXT("17.4");
```

> 来源：`CaptureManagerTakeMetadata/Public/CaptureManagerTakeMetadata.h`

### 进阶用法 — 缩略图数据流转

典型的缩略图数据流转场景（从设备接收 → 存储 → 编辑器展示）：

```cpp
// 1. DataIngestCore 从设备接收到缩略图数据后构造
TArray<uint8> ReceivedData = NetworkReceiveThumbnail();
FTakeThumbnailData Thumbnail(MoveTemp(ReceivedData));

// 2. 保存到 Take 元数据
FTakeMetadata TakeMetadata;
// ... 设置 TakeMetadata 的其他字段 ...
// TakeMetadata 通过序列化写入 .take 文件

// 3. Capture Manager Editor 读取后展示
TOptional<TArray<uint8>> DisplayData = Thumbnail.GetThumbnailData();
if (DisplayData.IsSet())
{
    // 将 DisplayData 传给 UTexture2D 或 Slate Brush 进行渲染
}

// 4. 如果有本地文件路径，也可以直接使用路径
TOptional<FString> LocalPath = Thumbnail.GetThumbnailPath();
if (LocalPath.IsSet())
{
    // 直接从磁盘加载，避免内存拷贝
}
```

## Demo 示例

### 最小 Take 元数据使用示例

```cpp
// MyTakeProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "CaptureManagerTakeMetadata.h"

class FMyTakeProcessor
{
public:
    /** 创建一个带缩略图的 Take 元数据示例 */
    static FTakeMetadata CreateSampleTake()
    {
        FTakeMetadata Take;

        // 设置 Schema 版本
        FTakeMetadata::FSchemaVersion Version;
        Version.Major = 1;
        Version.Minor = 0;

        // 设置设备信息
        FTakeMetadata::FDevice Device;
        Device.FPlatform PlatformInfo;
        PlatformInfo.Name = TEXT("iPhone 15 Pro");
        PlatformInfo.Version = TEXT("17.4");

        return Take;
    }

    /** 从文件加载缩略图 */
    static FTakeThumbnailData LoadThumbnail(const FString& ImagePath)
    {
        return FTakeThumbnailData(ImagePath);
    }

    /** 从网络数据构造缩略图 */
    static FTakeThumbnailData CreateThumbnailFromNetworkData(TArray<uint8>&& CompressedData)
    {
        return FTakeThumbnailData(MoveTemp(CompressedData));
    }
};
```

```cpp
// MyTakeProcessor.cpp
#include "MyTakeProcessor.h"

// 所有方法均在头文件中以内联方式实现
// 此文件可留空或添加额外的辅助实现
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ImageCore` | 图像格式定义（`ERawImageFormat`、`FColor` 等） |

无其他特殊依赖（仅标准 Core/CoreUObject 等）。

## 维护状态

### 近期更新

```
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- 44e6d35d1831 Thumbnail extraction with more formats supported
- e746610a5aea Implement simple stereo video device for Capture Manager Add thumbnail support for mono and stereo video devices Rename {UserId} discovery token to {Name} for video and audio components
```

- `2739c3d` — 代码规范化，修正 DLL 导出标记位置（API 宏放在方法上而非类型上）
- `44e6d35` — 扩展缩略图支持的图像格式
- `e746610` — 新增立体视频设备支持，为单目/立体视频设备添加缩略图功能，重命名发现令牌

### 维护评价

- **创建时间**：2025-02-04，非常新的插件（约 5 个月）
- **活跃度**：活跃开发中，近期有多次功能性更新（缩略图格式扩展、立体视频支持）
- **状态**：作为 Capture Manager 系统的核心模块，随上层插件同步维护
- **推荐**：✅ 该模块结构清晰、职责单一，适合作为 Take 数据格式的标准定义。但作为基础设施模块，通常不直接使用，而是通过 Capture Manager App/Editor 间接依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [CaptureManagerTakeMetadata 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureManagerTakeMetadata)