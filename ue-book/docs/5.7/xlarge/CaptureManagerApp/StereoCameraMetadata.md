# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是一个面向虚拟制片（Virtual Production）的**采集设备管理与数据处理平台**。它解决的核心问题是：在虚拟制片工作流中，如何统一地控制、监控各类采集设备（如 Live Link Face 面部捕捉 App、立体相机等），并将采集到的原始数据经过转码、元数据解析后，上传至 Unreal Engine 进行导入。

该插件并非单一功能模块，而是一个**完整的采集管理应用框架**，包含 11 个子模块，覆盖了从设备连接、数据读写、格式转码、处理管线到 UE 端点上传的全链路。

**核心能力**：
- **设备控制与监控**：通过 Live Link 协议连接和管理采集设备
- **数据获取与转码**：从设备获取原始采集数据并进行格式转换
- **元数据解析**：支持 Live Link Face 和立体相机等多种采集格式的元数据解析
- **数据上传**：将处理后的数据上传至 UE 进行资产导入
- **管线编排**：通过 Pipeline 模块编排数据处理流程

## 使用场景

- 你在做虚拟制片项目，需要从 iPhone 的 Live Link Face App 采集面部动画数据 → 使用 CaptureManagerApp 管理采集流程
- 你有一组立体相机采集的镜头数据，需要解析元数据并导入 UE → 使用 StereoCameraMetadata 模块
- 你需要将采集到的原始视频/音频数据转码为 UE 可用格式 → 使用 CaptureDataConverter 和 CaptureManagerMediaRW 模块
- 你需要将处理完成的采集数据自动上传到 Unreal Engine → 使用 CaptureManagerUnrealEndpoint 模块
- 你需要自定义采集设备的 Live Link 集成 → 参考 ExampleLiveLinkDevices 模块

## 模块架构

```
CaptureManagerApp/
├── CaptureManagerSettings        # 全局设置与配置
├── CaptureManagerPipeline        # 数据处理管线编排
├── CaptureManagerMediaRW         # 媒体数据读写
├── CaptureDataConverter          # 数据格式转码
├── CaptureManagerEditor          # 编辑器 UI 与交互
├── CaptureManagerUnrealEndpoint  # UE 端点上传
├── LiveLinkCapabilities          # Live Link 能力定义
├── LiveLinkFaceMetadata          # Live Link Face 元数据解析
├── StereoCameraMetadata          # 立体相机元数据解析
├── IngestLiveLinkDevice          # 数据导入 Live Link 设备
└── ExampleLiveLinkDevices        # 示例 Live Link 设备实现
```

## 蓝图用法

本插件的核心功能主要通过 C++ API 暴露。StereoCameraMetadata 等底层模块的函数为命名空间级别的 C++ 工具函数，未标记为 `BlueprintCallable`。编辑器交互功能集中在 `CaptureManagerEditor` 模块中（详细蓝图节点需参考该模块文档）。

## C++ 用法

### StereoCameraMetadata 模块

#### 头文件引入

```cpp
#include "StereoCameraMetadataParseUtils.h"
```

#### 基本用法 — 解析旧版立体相机元数据

```cpp
#include "StereoCameraMetadataParseUtils.h"

void ParseStereoCameraTake(const FString& TakeFolder)
{
    TArray<FText> ValidationErrors;
    
    TOptional<FTakeMetadata> Metadata = 
        UE::CaptureManager::StereoCameraMetadata::ParseOldStereoCameraMetadata(
            TakeFolder, 
            ValidationErrors
        );
    
    if (Metadata.IsSet())
    {
        // 解析成功，使用元数据
        const FTakeMetadata& TakeMetadata = Metadata.GetValue();
        // ... 处理 TakeMetadata
    }
    else
    {
        // 解析失败，检查验证错误
        for (const FText& Error : ValidationErrors)
        {
            UE_LOG(LogTemp, Warning, TEXT("Metadata validation error: %s"), *Error.ToString());
        }
    }
}
```

**说明**：
- `ParseOldStereoCameraMetadata` 用于解析**旧版格式**的立体相机采集元数据，提供向后兼容支持
- 输入参数 `InTakeFolder` 为采集数据所在的文件夹路径
- 输出参数 `OutValidationError` 收集解析过程中的验证错误信息
- 返回 `TOptional<FTakeMetadata>`：解析成功时包含元数据，失败时为空

#### 进阶用法 — 结合多模块处理采集数据

```cpp
#include "StereoCameraMetadataParseUtils.h"
#include "CaptureManagerTakeMetadata.h"

// 典型工作流：解析元数据 → 验证 → 转码 → 上传
void ProcessCaptureTake(const FString& TakeFolder)
{
    // 1. 解析立体相机元数据
    TArray<FText> Errors;
    TOptional<FTakeMetadata> Metadata = 
        UE::CaptureManager::StereoCameraMetadata::ParseOldStereoCameraMetadata(
            TakeFolder, Errors);
    
    if (!Metadata.IsSet())
    {
        for (const auto& Err : Errors)
        {
            UE_LOG(LogTemp, Error, TEXT("%s"), *Err.ToString());
        }
        return;
    }
    
    // 2. 使用元数据进行后续处理（转码、上传等）
    // ... 调用 CaptureDataConverter / CaptureManagerPipeline 等模块
}
```

## Demo 示例

### 最小可编译示例 — 解析立体相机元数据

**MyStereoCameraProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyStereoCameraProcessor
{
public:
    /** 解析指定采集文件夹中的立体相机元数据 */
    static bool ProcessTakeFolder(const FString& InTakeFolder, FString& OutErrorMessage);
};
```

**MyStereoCameraProcessor.cpp**
```cpp
#include "MyStereoCameraProcessor.h"
#include "StereoCameraMetadataParseUtils.h"

bool FMyStereoCameraProcessor::ProcessTakeFolder(
    const FString& InTakeFolder, 
    FString& OutErrorMessage)
{
    TArray<FText> ValidationErrors;
    
    TOptional<FTakeMetadata> Metadata = 
        UE::CaptureManager::StereoCameraMetadata::ParseOldStereoCameraMetadata(
            InTakeFolder, 
            ValidationErrors
        );
    
    if (!Metadata.IsSet())
    {
        // 汇总所有验证错误
        for (const FText& Error : ValidationErrors)
        {
            OutErrorMessage += Error.ToString() + TEXT("\n");
        }
        return false;
    }
    
    // 元数据解析成功
    const FTakeMetadata& Take = Metadata.GetValue();
    UE_LOG(LogTemp, Log, TEXT("Successfully parsed stereo camera metadata from: %s"), 
        *InTakeFolder);
    
    return true;
}
```

## 模块依赖

由于未提供 Build.cs 完整内容，以下为基于头文件包含关系推断的依赖：

| 模块 | 用途 |
|---|---|
| `CaptureManagerTakeMetadata` | 提供 `FTakeMetadata` 结构体定义（StereoCameraMetadata 的核心依赖） |

> 注：完整依赖列表需参考各模块的 `.Build.cs` 文件。该插件内部模块之间存在交叉依赖关系。

## 维护状态

### 近期更新

```
- bd59a22f1783 [CaptureManager] Replace UserId with Name in take metadata
- 281329a6f604 Delete the Capture Source framework as it will not be used anymore
- d8866975645a CaptureManager: Move plugin to Virtual Production directory
```

- **bd59a22f**：元数据结构变更，将 UserId 字段替换为 Name，属于 API 变更
- **281329a6**：删除了 Capture Source 框架，表明架构正在重构简化
- **d8866975**：将插件从原位置迁移至 Virtual Production 目录，属于项目组织调整

### 维护评价

- **创建时间**：2025-02-04，非常新的插件（约 5 个月）
- **活跃度**：近期有实质性架构变更（删除 Capture Source 框架、API 字段重命名），表明处于**积极开发阶段**
- **稳定性**：作为新插件，API 尚未稳定（UserId → Name 的变更说明接口仍在演进）
- **风险提示**：⚠️ 该插件非常新，API 可能会发生变化。在生产环境中使用时需关注版本更新
- **推荐程度**：如果你的项目涉及虚拟制片采集工作流，这是 Epic 官方提供的标准解决方案，**推荐使用**，但需做好 API 变更的准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [官方文档]()（暂无）