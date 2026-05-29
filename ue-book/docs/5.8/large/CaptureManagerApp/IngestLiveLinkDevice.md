# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 中文名 | 采集管理器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（示例设备配置） |
| 模块 | `CaptureManagerEditor` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是虚拟制片管线中的**数据采集与导入工具链**。它解决的核心问题是：如何将外部采集设备（如动作捕捉设备、体积摄影设备等）产生的原始数据，经过转码、转换后，自动上传并导入到 Unreal Engine 中。

具体来说，这个插件提供了：

1. **设备发现与控制**：通过 LiveLink 设备框架连接和管理采集设备，监控设备状态
2. **Take 数据管理**：枚举、选择、管理采集设备上的 Take（采集片段）数据
3. **数据转码**：将设备原始格式（如专有视频编码）转码为 UE 可接受的格式
4. **数据导入**：将转码后的数据上传至 UE 并触发自动导入流程

整个插件以 LiveLink 设备能力框架为基础，`IngestLiveLinkDevice` 模块提供了数据导入的抽象基类，`LiveLinkCapabilities` 定义了设备能力接口，`ExampleLiveLinkDevices` 则给出了具体实现参考。

## 使用场景

- 你在搭建虚拟制片的采集管线，需要将体积摄影/动捕设备的数据自动导入 UE → 用 CaptureManagerApp
- 你需要开发自定义的 LiveLink 采集设备插件，支持数据下载、转码和上传 → 继承 `UBaseIngestLiveLinkDevice`
- 你需要管理多个采集设备的 Take 数据生命周期（枚举→下载→转码→上传→导入）→ 使用 Ingest Capability 框架
- 你在做现场虚拟制片，需要实时监控采集设备状态并控制采集流程 → 使用设备控制 API

## 蓝图用法

本插件的核心类 `UBaseIngestLiveLinkDevice` 是一个 **C++ 抽象基类**，主要通过 C++ 子类化使用。蓝图层面主要通过继承自 `ULiveLinkDevice` 的接口进行设备管理。

### 核心节点

由于本模块定义的是抽象基类，没有直接暴露的 `BlueprintCallable` 节点。设备交互通过 LiveLink 设备面板和设备能力系统在编辑器中完成。

| 功能 | 说明 | 所在类 |
|---|---|---|
| 设备添加/移除回调 | 设备生命周期管理 | `UBaseIngestLiveLinkDevice` |
| 数据导入流程 | 下载→转码→上传的完整管线 | `ILiveLinkDeviceCapability_Ingest` |

### 使用示例（编辑器工作流）

1. 在 **LiveLink 面板**中添加采集设备
2. 设备会自动注册并开始监控
3. 通过设备面板浏览可用的 Take 列表
4. 选择 Take 并触发导入（自动执行转码和上传）

## C++ 用法

### 头文件引入

```cpp
#include "BaseIngestLiveLinkDevice.h"
```

### 基本用法

自定义 LiveLink 采集设备的最小实现，继承 `UBaseIngestLiveLinkDevice` 并实现所有纯虚函数：

```cpp
// MyCaptureDevice.h
#pragma once

#include "BaseIngestLiveLinkDevice.h"
#include "MyCaptureDevice.generated.h"

UCLASS()
class UMyCaptureDevice : public UBaseIngestLiveLinkDevice
{
    GENERATED_BODY()

public:
    // 返回设备上指定 Take 数据的完整路径
    virtual FString GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const override
    {
        // 根据 TakeId 构造设备上的文件路径
        return FString::Printf(TEXT("DevicePath/Takes/%d"), InTakeId);
    }

    // 实现下载逻辑
    virtual void RunDownloadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override
    {
        // 调用基类的 IngestTake 处理默认流程
        // 或实现自定义下载逻辑
    }

    // 实现转码和上传逻辑
    virtual void RunConvertAndUploadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override
    {
        // 实现转码和上传到 UE 的逻辑
    }

    // 实现 Take 列表更新
    virtual void RunUpdateTakeList(
        UIngestCapability_UpdateTakeListCallback* InCallback) override
    {
        // 从设备获取最新 Take 列表并回调
        if (InCallback)
        {
            // InCallback->Execute(UpdatedTakeList);
        }
    }
};
```

> 来源：`Source/IngestLiveLinkDevice/Public/BaseIngestLiveLinkDevice.h`

### 进阶用法

使用基类提供的 `IngestTake()` 辅助方法简化导入流程，以及使用错误处理工具函数：

```cpp
// 在 RunDownloadTake 或 RunConvertAndUploadTake 中使用基类默认实现
void UMyCaptureDevice::RunDownloadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions)
{
    // 使用基类提供的 IngestTake 进行标准的转码和上传
    auto TaskProgress = MakeShared<UE::CaptureManager::FTaskProgress>();
    IngestTake(InProcessHandle, InIngestOptions, TaskProgress);
}

// 使用错误处理工具
#include "IngestLiveLinkDeviceUtils.h"

FString ErrorText = UE::CaptureManager::ErrorOriginToString(
    FTakeMetadataParserError::EOrigin::SomeOrigin);
```

> 来源：`Source/IngestLiveLinkDevice/Public/Utils/IngestLiveLinkDeviceUtils.h`

## Demo 示例

一个完整的可编译最小示例——自定义采集设备：

```cpp
// SimpleCaptureDevice.h
#pragma once

#include "BaseIngestLiveLinkDevice.h"
#include "SimpleCaptureDevice.generated.h"

/**
 * 最简采集设备示例：模拟从本地文件夹"采集"数据
 */
UCLASS()
class USimpleCaptureDevice : public UBaseIngestLiveLinkDevice
{
    GENERATED_BODY()

protected:
    // Take 数据的基础目录
    UPROPERTY(EditAnywhere, Category = "Capture")
    FString BaseTakeDirectory = TEXT("C:/Captures");

    virtual FString GetFullTakePath(UE::CaptureManager::FTakeId InTakeId) const override
    {
        return FPaths::Combine(BaseTakeDirectory, FString::FromInt(InTakeId));
    }

    virtual void RunDownloadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override
    {
        // 本地文件无需下载，直接标记完成
    }

    virtual void RunConvertAndUploadTake(
        const UIngestCapability_ProcessHandle* InProcessHandle,
        const UIngestCapability_Options* InIngestOptions) override;

    virtual void RunUpdateTakeList(
        UIngestCapability_UpdateTakeListCallback* InCallback) override;
};
```

```cpp
// SimpleCaptureDevice.cpp
#include "SimpleCaptureDevice.h"
#include "IngestLiveLinkDeviceLog.h"

DEFINE_LOG_CATEGORY(LogIngestLiveLinkDevice);

void USimpleCaptureDevice::RunConvertAndUploadTake(
    const UIngestCapability_ProcessHandle* InProcessHandle,
    const UIngestCapability_Options* InIngestOptions)
{
    // 使用基类的默认转码上传流程
    auto Progress = MakeShared<UE::CaptureManager::FTaskProgress>();
    IngestTake(InProcessHandle, InIngestOptions, Progress);

    UE_LOG(LogIngestLiveLinkDevice, Log,
        TEXT("SimpleCaptureDevice: Convert and upload completed."));
}

void USimpleCaptureDevice::RunUpdateTakeList(
    UIngestCapability_UpdateTakeListCallback* InCallback)
{
    // 扫描 BaseTakeDirectory 获取可用 Take 列表
    // 构造 Take 元数据并通过回调返回
    if (InCallback)
    {
        // 实际实现中扫描目录并填充 Take 列表
        UE_LOG(LogIngestLiveLinkDevice, Log,
            TEXT("SimpleCaptureDevice: Take list updated."));
    }
}
```

## 模块依赖

从各模块的 Build.cs 和类继承关系推断，以下为该插件**独特**的依赖关系：

| 模块 | 用途 |
|---|---|
| `CaptureManagerCore` | 提供 Take 元数据、任务进度、转码管线等核心功能 |
| `LiveLink` | 基础 LiveLink 设备框架（`ULiveLinkDevice` 基类） |
| `LiveLinkCapabilities` | 设备能力接口定义（`ILiveLinkDeviceCapability_Ingest`） |
| `UnrealEd` | 编辑器集成（LiveLinkCapabilities 模块依赖） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 向核心模块添加 CPS 客户端功能 |
| 2026-04-28 | `6eba47f3` | [Capture Manager] Warn when Third Party Encoder is required for ingest | 数据采集需要第三方编码器时增加警告提示 |
| 2026-04-23 | `43d97726` | MediaProfile: Moved UMediaProfile and related entities to its own plugin to avoid dependency on Open | 将 MediaProfile 迁移至独立插件以减少耦合 |
| 2026-04-20 | `a8e2df25` | [CaptureManager] Add auto-rotation mode to ECaptureManagerRotation | 添加自动旋转模式支持 |
| 2026-04-16 | `cf2dffa4` | [CaptureManager] Fix broken LLH encoder defaults. | 修复 LLH 编码器的默认配置错误 |

### 维护评价

- **活跃维护**：最近一个月内有多次实质性功能更新和 Bug 修复
- **Epic 官方维护**：由 Epic Games 的虚拟制片团队持续开发
- **功能扩展中**：正在积极添加新能力（CPS 客户端、旋转模式、编码器改进）
- **依赖优化进行中**：正在解耦模块依赖（MediaProfile 迁移）
- **推荐使用**：作为 Epic 官方虚拟制片工具链的一部分，适合在正式项目中使用。但由于是相对较新的插件（约 1 年），API 可能仍有变动，建议关注版本更新日志

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [官方文档]()（暂无）