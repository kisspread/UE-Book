# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureManagerEditor` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是一个用于虚拟制片工作流的捕获管理应用。它的核心功能是管理和监控捕获设备（如相机、传感器等），从这些设备中获取原始数据，对数据进行转码处理（如视频编码、音频编码），然后将处理后的数据上传到 Unreal Engine 中进行导入。它本质上是一个专业的**数据采集、处理和导入流水线**，旨在自动化虚拟制片中从物理设备到数字资产的转换过程。

## 使用场景

- 你在进行虚拟制片拍摄，需要从动作捕捉、多角度摄像机等设备中集中采集数据
- 你需要将采集到的大量原始视频/音频数据统一转码为引擎可高效处理的格式
- 你希望自动化地将转码后的数据上传并导入到 UE 项目中，用于实时合成或后期制作

## 蓝图用法

由于插件的核心功能是数据处理流水线，蓝图直接交互的 API 相对有限。从 `CaptureManagerSettings` 模块分析，主要的蓝图可访问功能集中在配置和设置层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetGeneralNamingTokens` | 获取用于生成文件名等的通用命名令牌对象 | `UCaptureManagerSettings` |
| `GetVideoEncoderNamingTokens` | 获取用于视频编码文件命名的令牌对象 | `UCaptureManagerSettings` |
| `GetAudioEncoderNamingTokens` | 获取用于音频编码文件命名的令牌对象 | `UCaptureManagerSettings` |

*注意：以上函数返回对象指针，主要供内部系统使用。蓝图用户通常通过修改设置资产来配置插件。*

### 使用示例（蓝图描述）

在蓝图中，你通常不直接调用上述节点，而是通过访问“项目设置”或“编辑器偏好设置”中的 **Capture Manager** 类别，修改其全局设置（如默认工作目录、是否使用第三方编码器等）。这些设置将被插件的其他模块自动读取和使用。

## C++ 用法

### 头文件引入

```cpp
#include "Settings/CaptureManagerSettings.h"
```

### 基本用法

访问和读取 Capture Manager 的全局设置。

```cpp
// 来源: Source/CaptureManagerSettings/Public/Settings/CaptureManagerSettings.h
// 获取全局设置单例
UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>();
if (Settings)
{
    // 读取默认工作目录
    FDirectoryPath WorkingDir = Settings->DefaultWorkingDirectory;
    UE_LOG(LogTemp, Log, TEXT("默认工作目录: %s"), *WorkingDir.Path);

    // 检查是否启用了第三方编码器
    bool bUseThirdParty = Settings->bEnableThirdPartyEncoder;
    if (bUseThirdParty)
    {
        // 获取第三方编码器的路径
        FFilePath EncoderPath = Settings->ThirdPartyEncoder;
        UE_LOG(LogTemp, Log, TEXT("使用第三方编码器: %s"), *EncoderPath.FilePath);
    }

    // 获取并行处理作业数
    int32 ParallelJobs = Settings->NumIngestExecutors;
    UE_LOG(LogTemp, Log, TEXT("并行作业数: %d"), ParallelJobs);
}
```

### 进阶用法

使用插件提供的命名令牌系统来动态构建文件名模板。

```cpp
#include "Settings/CaptureManagerTemplateTokens.h"

// 来源: Source/CaptureManagerSettings/Public/Settings/CaptureManagerTemplateTokens.h
// 获取通用命名令牌
UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>();
TObjectPtr<UCaptureManagerGeneralTokens> GeneralTokens = Settings->GetGeneralNamingTokens();
if (GeneralTokens)
{
    // 假设有一个令牌键值对映射
    TMap<FString, FString> TokenMap;
    TokenMap.Add(TEXT("ProjectName"), TEXT("MyProject"));
    TokenMap.Add(TEXT("TakeNumber"), TEXT("001"));

    // 使用令牌生成一个文件名（具体方法可能因版本而异，此为示意）
    FString GeneratedName = GeneralTokens->ApplyTokens(TEXT("ProjectName_TakeNumber"), TokenMap);
    UE_LOG(LogTemp, Log, TEXT("生成的文件名: %s"), *GeneratedName);
}
```

## Demo 示例

以下示例展示如何在编辑器模块中正确注册并响应 Capture Manager 设置的变更。

```cpp
// MyEditorModule.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnCaptureManagerSettingsChanged(UObject* InObject, struct FPropertyChangedEvent& InPropertyChangedEvent);
    FDelegateHandle SettingsChangeDelegateHandle;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "Settings/CaptureManagerSettings.h"

void FMyEditorModule::StartupModule()
{
    // 监听设置变更
    if (UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>())
    {
        SettingsChangeDelegateHandle = Settings->OnObjectModified.AddRaw(this, &FMyEditorModule::OnCaptureManagerSettingsChanged);
    }
}

void FMyEditorModule::ShutdownModule()
{
    // 移除监听
    if (UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>())
    {
        Settings->OnObjectModified.Remove(SettingsChangeDelegateHandle);
    }
}

void FMyEditorModule::OnCaptureManagerSettingsChanged(UObject* InObject, FPropertyChangedEvent& InPropertyChangedEvent)
{
    // 当设置属性变更时执行
    UE_LOG(LogTemp, Log, TEXT("Capture Manager 设置已更新。"));

    // 检查具体是哪个属性变更
    if (InPropertyChangedEvent.GetPropertyName() == GET_MEMBER_NAME_CHECKED(UCaptureManagerSettings, bEnableThirdPartyEncoder))
    {
        bool bNewValue = InObject->GetPropertyValue<bool>(InPropertyChangedEvent.MemberProperty);
        UE_LOG(LogTemp, Log, TEXT("第三方编码器设置更改为: %s"), bNewValue ? TEXT("启用") : TEXT("禁用"));
    }
}
```

## 模块依赖

从 `CaptureManagerSettings` 模块的 `Build.cs` 分析，其主要依赖为标准核心模块。该插件的其他模块可能有更复杂的依赖，但设置模块相对独立。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于 `LiveLinkCapabilities` 模块，提供编辑器功能 |
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 用于 `CaptureManagerSettings` 模块本身 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 在CaptureManagerCore中增加了CPS客户端模块 |
| 2026-04-28 | `6eba47f3` | [Capture Manager] Warn when Third Party Encoder is required for ingest | 当导入过程需要第三方编码器时发出警告 |
| 2026-04-23 | `43d97726` | MediaProfile: Moved UMediaProfile and related entities to its own plugin to avoid dependency on Open | 将媒体配置文件移至独立插件，减少对Open的依赖 |
| 2026-04-20 | `a8e2df25` | [CaptureManager] Add auto-rotation mode to ECaptureManagerRotation | 为捕获管理器旋转模式添加了自动旋转选项 |
| 2026-04-16 | `cf2dffa4` | [CaptureManager] Fix broken LLH encoder defaults. | 修复了LiveLink Hub编码器默认值损坏的问题 |

### 维护评价

- **活跃维护**：插件创建于 2025 年初，距今约 1 年，且近期（2026年4月）仍有密集的功能更新和 Bug 修复，表明处于**非常活跃**的开发阶段。
- **核心功能**：从更新日志看，开发团队持续在增强核心功能（新增编码客户端、旋转模式）和修复关键问题（编码器默认值、依赖重构）。
- **推荐度**：**强烈推荐**给从事虚拟制片项目的团队。它提供了一个标准化的数据采集处理流程，能显著提升工作效率。由于更新活跃，建议跟随最新版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [官方文档]() (暂无)
- [测试用例]() (暂无公开测试用例链接)