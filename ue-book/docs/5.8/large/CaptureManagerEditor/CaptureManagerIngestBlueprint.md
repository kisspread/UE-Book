# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、核心逻辑） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

CaptureManagerEditor 是一个面向虚拟制片工作流的**数据摄取与管理编辑器插件**。它解决的核心问题是：**将来自不同捕获设备（如LiveLink Face iPhone应用、立体相机、单目相机等）的原始捕获数据（视频、音频、校准文件、Take归档）转换并导入为UE/UEFN可用的资产**。

这个插件存在的意义在于统一并自动化捕获数据的导入流程。在没有此类工具的情况下，用户需要手动处理不同格式的文件、进行格式转换、管理文件路径和命名，过程繁琐且容易出错。CaptureManagerEditor 提供了蓝图和C++ API，让用户可以通过简单的函数调用或蓝图节点，一键完成从原始媒体文件到 `FootageCaptureData` 资产的转换，大大提高了虚拟制片工作流的效率。

**注意：** 该插件默认未启用（`EnabledByDefault: false`），需要在项目设置或插件界面手动启用。

## 使用场景

- **从iPhone的LiveLink Face应用导入面部捕捉数据**：当你使用LiveLink Face应用录制了面部表情数据后，可以直接将录制目录拖入或通过路径导入，插件会自动处理视频、音频和面部追踪数据。
- **导入双机立体视频素材**：如果你使用两台相机同步拍摄（用于创建深度信息或立体内容），可以将两个视频文件路径和可选的校准文件一起导入。
- **处理`.cptake`格式的Take归档**：某些捕获系统或设备（如Meta的设备）会生成包含所有必要元数据的`.cptake`压缩包。本插件可以直接解析并导入这种归档。
- **批量扫描和导入目录中的捕获素材**：使用 `FindTakeDirectories` 节点可以快速扫描一个目录，找出其中所有可识别的捕获素材（视频、图片序列、音频等），然后根据返回的信息批量进行导入。
- **在自定义工具或编辑器扩展中集成捕获数据导入功能**：开发者可以利用提供的C++ API，在自定义的编辑器工具或管线中集成数据导入逻辑。

## 蓝图用法

核心功能集中在 `UCaptureManagerIngestBlueprintLibrary` 这个蓝图函数库中。所有导入操作都支持同步和异步两种模式。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Ingest Take Archive` | 同步导入 `.cptake` 归档文件，返回 `FootageCaptureData` 资产指针 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Take Archive (Async)` | 异步导入 `.cptake` 归档文件，通过委托返回结果或错误 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Mono Video` | 同步导入单目视频文件（.mp4, .mov），返回 `FootageCaptureData` 资产指针 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Mono Video (Async)` | 异步导入单目视频文件 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Stereo Video` | 同步导入双机立体视频（支持两个视频文件或两个图片序列文件夹），返回 `FootageCaptureData` 资产指针 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Stereo Video (Async)` | 异步导入双机立体视频 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Live Link Face` | 同步导入LiveLink Face捕获目录，返回 `FootageCaptureData` 资产指针 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Live Link Face (Async)` | 异步导入LiveLink Face捕获目录 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Calibration` | 同步导入独立的校准文件（.json），返回包含校准信息的 `FootageCaptureData` 资产指针 | `UCaptureManagerIngestBlueprintLibrary` |
| `Ingest Calibration (Async)` | 异步导入独立的校准文件 | `UCaptureManagerIngestBlueprintLibrary` |
| `Cancel Ingest` | 根据异步操作返回的 `IngestId` 取消一个排队中或正在运行的导入任务 | `UCaptureManagerIngestBlueprintLibrary` |
| `Find Take Directories` | 扫描指定目录，返回一个包含所有可识别捕获素材目录信息的数组 | `UCaptureManagerIngestBlueprintLibrary` |

### 使用示例（蓝图描述）

**示例1：同步导入单个视频文件**
1. 获取一个视频文件的完整路径（例如 `C:\Captures\Video_001.mp4`）。
2. 创建一个 `FCaptureManagerConversionParams` 结构体变量，设置输出图片格式（如 PNG）、音频格式（如 WAV）和旋转模式（通常为 Auto）。
3. 调用 `Ingest Mono Video` 节点。
4. 将视频路径、可选的音频路径（留空）、Slate名称（如从文件名推导）、Take编号（默认1）和转换参数连接到节点输入。
5. 节点执行成功后，其返回值（`FootageCaptureData`）即为新创建的资产引用，可以将其保存到Content Browser或用于后续处理。
6. 如果失败，`OutErrorMessage` 输出参数会包含错误描述。

**示例2：异步批量导入并处理完成事件**
1. 调用 `Find Take Directories` 节点，传入一个根目录（如 `C:\AllCaptures\`），并勾选 `bRecursive`。
2. 遍历返回的目录信息数组。
3. 对于每个目录信息（`FCaptureManagerTakeDirectoryInfo`），根据其 `bIsTakeArchive`、`bIsLiveLinkFace` 等标志选择对应的异步导入函数（如 `Ingest Take Archive (Async)`）。
4. 为每个异步调用绑定 `OnSuccess` 和 `OnFailure` 委托。
5. 在 `OnSuccess` 委托中，你可以接收 `FootageCaptureData` 指针并进行后续操作（如应用到场景中的角色上）。
6. 如果需要取消某个任务，保存 `Ingest Take Archive (Async)` 返回的 `IngestId`，然后在需要时调用 `Cancel Ingest` 并传入该ID。

## C++ 用法

C++ API 主要用于需要高性能、更精细控制或集成到自定义编辑器模块中的场景。

### 头文件引入

```cpp
#include "CaptureManagerIngestBlueprintLibrary.h"
```

### 基本用法

以下示例展示了如何使用同步API导入一个Take归档。

```cpp
// 来自 Private/CaptureManagerIngestBlueprintLibrary.h 中的函数声明
// 假设我们有一个 Take 归档的路径
FString TakeArchivePath = TEXT("/Path/To/MyTake.cptake");

// 设置转换参数
FCaptureManagerConversionParams Params;
Params.ImageFormat = ECaptureManagerImageFormat::Png;
Params.AudioFormat = ECaptureManagerAudioFormat::Wav;
Params.Rotation = ECaptureManagerRotation::Auto;

FText ErrorMessage;
// 调用同步导入函数
UFootageCaptureData* FootageCaptureData = UCaptureManagerIngestBlueprintLibrary::IngestTakeArchiveSync(
    TakeArchivePath,
    Params,
    ErrorMessage
);

if (FootageCaptureData)
{
    // 导入成功，可以使用 FootageCaptureData 资产
    UE_LOG(LogTemp, Log, TEXT("成功导入Take归档，资产名称: %s"), *FootageCaptureData->GetName());
}
else
{
    // 导入失败，打印错误信息
    UE_LOG(LogTemp, Error, TEXT("导入失败: %s"), *ErrorMessage.ToString());
}
```

### 进阶用法

以下示例展示了如何使用异步API并处理取消操作。

```cpp
#include "CaptureManagerIngestBlueprintLibrary.h"
#include "Delegates/DelegateSignatureImpl.inl" // 用于绑定动态多播委托

// 1. 定义成功和失败的回调函数
void OnIngestSuccess(int32 IngestId, ECaptureManagerIngestType IngestType, UFootageCaptureData* FootageCaptureData)
{
    UE_LOG(LogTemp, Log, TEXT("异步导入成功，IngestId: %d, 类型: %s"), IngestId, *UEnum::GetValueAsString(IngestType));
    // 在这里处理导入成功的资产，例如保存它
    // FAssetRegistryModule::AssetCreated(FootageCaptureData);
}

void OnIngestFailed(int32 IngestId, ECaptureManagerIngestType IngestType, FText ErrorMessage)
{
    UE_LOG(LogTemp, Error, TEXT("异步导入失败，IngestId: %d, 类型: %s, 错误: %s"),
        IngestId, *UEnum::GetValueAsString(IngestType), *ErrorMessage.ToString());
}

// 2. 启动异步导入
FString VideoPath = TEXT("/Path/To/Video.mp4");
FCaptureManagerConversionParams Params;
FCaptureManagerIngestSuccess SuccessDelegate;
FCaptureManagerIngestFailed FailureDelegate;

SuccessDelegate.BindDynamic(&OnIngestSuccess); // 假设在某个 UObject 上下文中
FailureDelegate.BindDynamic(&OnIngestFailed);  // 假设在某个 UObject 上下文中

int32 IngestId = UCaptureManagerIngestBlueprintLibrary::IngestMonoVideo(
    VideoPath,
    TEXT(""), // 空的音频路径
    TEXT(""), // 空的 Slate 名称
    1,        // Take编号
    Params,
    SuccessDelegate,
    FailureDelegate
);

// 3. 保存 IngestId 以便后续取消
ActiveIngestId = IngestId;

// 4. 在某个时机（例如用户点击取消按钮）取消任务
if (ActiveIngestId != -1)
{
    bool bCancelled = UCaptureManagerIngestBlueprintLibrary::CancelIngest(ActiveIngestId);
    if (bCancelled)
    {
        UE_LOG(LogTemp, Warning, TEXT("已取消 IngestId: %d 的任务"), ActiveIngestId);
    }
    ActiveIngestId = -1;
}
```

## Demo 示例

一个最小化的示例，展示如何从编辑器工具菜单触发一个视频导入，并在输出日志中显示结果。

**CaptureManagerDemoTool.h**
```cpp
// CaptureManagerDemoTool.h
#pragma once

#include "CoreMinimal.h"
#include "Toolkits/AssetEditorManager.h" // 用于编辑器工具

class FCaptureManagerDemoTool : public FAssetEditorToolkit
{
public:
    // 注册一个编辑器菜单扩展
    static void RegisterMenus();

    // 执行导入操作
    static void ExecuteImportTest();

    // IToolkit 接口
    virtual FName GetToolkitFName() const override { return TEXT("CaptureManagerDemoTool"); }
    virtual FText GetBaseToolkitName() const override { return FText::FromString(TEXT("Capture Manager Demo")); }
    virtual FLinearColor GetWorldCentricTabColorScale() const override { return FLinearColor::White; }
    virtual FString GetWorldCentricTabPrefix() const override { return TEXT("CM Demo"); }
};
```

**CaptureManagerDemoTool.cpp**
```cpp
// CaptureManagerDemoTool.cpp
#include "CaptureManagerDemoTool.h"
#include "CaptureManagerIngestBlueprintLibrary.h"
#include "ToolMenus.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"

void FCaptureManagerDemoTool::RegisterMenus()
{
    // 在编辑器的“工具”菜单下添加一个子菜单
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateLambda([]()
    {
        FToolMenuOwnerScoped OwnerScoped(UE_MODULE_NAME);
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
        FToolMenuSection& Section = Menu->AddSection("CaptureManagerDemoSection", FText::FromString(TEXT("Capture Manager Demo")));
        Section.AddMenuEntry(
            "TestImport",
            FText::FromString(TEXT("Test Mono Video Import")),
            FText::FromString(TEXT("Tests importing a hardcoded video path")),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateStatic(&FCaptureManagerDemoTool::ExecuteImportTest))
        );
    }));
}

void FCaptureManagerDemoTool::ExecuteImportTest()
{
    // 一个硬编码的测试路径，实际使用时应通过文件对话框让用户选择
    FString VideoPath = TEXT("D:/TestVideos/TestClip.mp4");

    FCaptureManagerConversionParams Params;
    Params.ImageFormat = ECaptureManagerImageFormat::Png;
    Params.Rotation = ECaptureManagerRotation::Auto;

    FText ErrorMessage;
    UFootageCaptureData* CaptureData = UCaptureManagerIngestBlueprintLibrary::IngestMonoVideoSync(
        VideoPath,
        TEXT(""), // 音频路径
        TEXT("TestSlate"), // Slate名称
        1, // Take编号
        Params,
        ErrorMessage
    );

    if (CaptureData)
    {
        UE_LOG(LogTemp, Display, TEXT("Demo Tool: Import successful! Asset created: %s"), *CaptureData->GetPathName());
        // 可以进一步操作，比如打开资产编辑器
        // FAssetEditorManager::Get().OpenEditorForAsset(CaptureData);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Demo Tool: Import failed. Error: %s"), *ErrorMessage.ToString());
    }
}
```

## 模块依赖

该插件由多个模块组成，但根据 `CaptureManagerIngestBlueprint` 模块的 `Build.cs` 分析，它主要依赖以下 **不常见的模块**。用户在自己模块中使用该插件功能时，需确保依赖相应模块。

| 模块 | 用途 |
|---|---|
| `CaptureManagerCore` | 提供捕获数据的核心数据结构（如 `UFootageCaptureData`、`FTakeMetadata`） |
| `CaptureManagerEditorSettings` | 提供插件编辑器设置（如并发导入数量、工作目录等）的访问 |
| `MediaUtils` | 处理媒体文件（视频、音频）的解析和转码 |
| `ImageWriteQueue` | 用于将图片序列异步写入磁盘 |
| `Tasks` | UE的任务系统，用于实现异步导入和取消功能 |
| `StopToken` | 提供任务取消的令牌机制 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 在设备蓝图模块中泛化设备术语，提升代码通用性 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将同步（阻塞式）导入蓝图API移至“Blocking”子分类，使蓝图节点组织更清晰 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 `CaptureManagerDeviceBlueprint` 模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回滚了某个改动（CL53274396） |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次添加 `CaptureManagerDeviceBlueprint` 模块（随后被回滚） |

### 维护评价

**维护状态：活跃维护**

- **创建时间**：2025年2月，插件非常新。
- **最近更新**：2026年4月30日有多次提交，表明插件仍在积极开发和重构中。最近的更新包括代码组织优化（API分类）和新功能模块的加入。
- **活跃度**：近期有持续的开发活动，属于活跃维护的插件。
- **已知问题/限制**：
    1.  插件默认未启用，需要用户手动启用。
    2.  文档中未提及官方文档链接（DocsURL为空），可能缺少详细的官方使用指南。
    3.  主要面向特定的虚拟制片工作流（如LiveLink Face），对其他捕获设备的支持情况需查看代码。
- **推荐使用**：**推荐**。对于需要处理捕获数据导入的虚拟制片项目，这是一个由Epic Games官方维护的、功能明确且正在积极改进的工具。对于新项目，建议采用其异步API以避免阻塞游戏线程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- 官方文档：暂无（.uplugin中DocsURL为空）
- 测试用例：在提供的源码信息中未发现专门的测试文件（Tests）。