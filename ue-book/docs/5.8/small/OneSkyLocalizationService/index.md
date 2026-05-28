# OneSky

> OneSky localization service

| 属性 | 值 |
|---|---|
| 中文名 | OneSky翻译服务 |
| 分类 | Localization |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OneSkyLocalizationService` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2015-05-22 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/OneSkyLocalizationService) | |

## 用途

本插件是 UE5 本地化服务框架（Localization Service）与 **OneSky** 云端翻译管理平台的集成桥接器。它解决了以下核心问题：

- **翻译外包协作**：将游戏中需要翻译的文本上传到 OneSky 平台，供专业翻译人员在线翻译和审核，完成后拉回引擎
- **翻译状态追踪**：在编辑器内实时查看每条翻译文本在 OneSky 上的状态（未翻译、未接受、未定稿、已定稿、已废弃等）
- **项目与文件管理**：通过编辑器内嵌 UI 直接管理 OneSky 上的项目组、项目、语言和文件，无需切换到浏览器

插件基于 UE 的 `ILocalizationServiceProvider` 接口实现，可以通过 OneSky 的 REST API 进行 HTTP 通信。插件标记为 **Beta** 且 **默认未启用**，属于实验性质的早期集成方案，部分功能（如删除操作）尚未实现。

## 使用场景

- 你的项目需要将本地化字符串批量提交给 OneSky 上的翻译团队进行多语言翻译
- 你需要在 UE 编辑器的本地化仪表板中直接查看翻译进度并一键拉取完成的翻译
- 你的团队使用 OneSky 作为翻译管理平台，希望减少手动导出/导入 .po 文件的工作量

## 蓝图用法

本插件不暴露任何蓝图接口。它完全作为编辑器服务（Editor Service）运行，通过本地化仪表板（Localization Dashboard）的工具栏按钮与用户交互。

### 编辑器 UI 功能

插件在本地化仪表板中注册了以下工具栏扩展：

| 功能 | 说明 |
|---|---|
| 导出到 OneSky | 将本地化目标的所有文化版本上传到 OneSky |
| 从 OneSky 导入 | 从 OneSky 下载所有文化版本的翻译并导入引擎 |
| 目标集批量操作 | 对目标集中的所有目标执行批量导入/导出 |

所有交互通过编辑器本地化面板的自定义工具栏按钮触发，无需蓝图代码。

## C++ 用法

本插件主要通过 `ILocalizationServiceProvider` 接口与本地化框架交互。以下是从源码中提取的核心 API 用法。

### 头文件引入

```cpp
#include "OneSkyLocalizationServiceProvider.h"
#include "OneSkyLocalizationServiceOperations.h"
#include "OneSkyLocalizationServiceSettings.h"
```

### 基本用法

获取插件实例和 Provider：

```cpp
// 来源: Source/OneSkyLocalizationService/Private/OneSkyLocalizationServiceModule.h

// 获取模块实例
FOneSkyLocalizationServiceModule& Module = FOneSkyLocalizationServiceModule::Get();

// 获取服务 Provider
FOneSkyLocalizationServiceProvider& Provider = Module.GetProvider();

// 配置 API 凭据
FOneSkyLocalizationServiceSettings& Settings = Module.AccessSettings();
Settings.SetApiKey(TEXT("your_api_key"));
Settings.SetApiSecret(TEXT("your_api_secret"));
Settings.SetSaveSecretKey(true);  // 警告：密钥将以明文保存
```

### 进阶用法

配置本地化目标与 OneSky 项目的映射关系：

```cpp
// 来源: Source/OneSkyLocalizationService/Private/OneSkyLocalizationServiceSettings.h

// 为目标设置 OneSky 项目 ID 和文件名
FGuid TargetGuid = MyLocalizationTarget->Settings.Guid;
Settings.SetSettingsForTarget(TargetGuid, 12345, TEXT("game_strings"));

// 读取目标设置
FOneSkyLocalizationTargetSetting* TargetSetting = Settings.GetSettingsForTarget(TargetGuid);
if (TargetSetting)
{
    int32 OneSkyProjectId = TargetSetting->OneSkyProjectId;
    FString OneSkyFileName = TargetSetting->OneSkyFileName;
}
```

执行 OneSky 操作（通过 Provider 接口）：

```cpp
// 来源: Source/OneSkyLocalizationService/Private/OneSkyLocalizationServiceProvider.h

// 创建列出项目组的操作
auto ListGroupsOp = MakeShared<FOneSkyListProjectGroupsOperation>();
ListGroupsOp->SetInStartPage(0);
ListGroupsOp->SetInItemsPerPage(50);

TArray<FLocalizationServiceTranslationIdentifier> TranslationIds;

// 同步执行操作
ELocalizationServiceOperationCommandResult::Type Result = Provider.Execute(
    ListGroupsOp,
    TranslationIds,
    ELocalizationServiceOperationConcurrency::Synchronous,
    FLocalizationServiceOperationComplete::CreateLambda(
        [](const FLocalizationServiceOperationRef& Op, ELocalizationServiceOperationCommandResult::Type OpResult)
        {
            if (OpResult == ELocalizationServiceOperationCommandResult::Succeeded)
            {
                UE_LOG(LogTemp, Log, TEXT("OneSky operation completed successfully"));
            }
        })
    );
```

翻译状态枚举（用于判断翻译进度）：

```cpp
// 来源: Source/OneSkyLocalizationService/Private/OneSkyLocalizationServiceState.h

// 翻译状态：Unknown / Untranslated / NotAccepted / NotFinalized / Finalized / Deprecated
EOneSkyState::Type State = MyState->GetState();

// 设置翻译内容
MyState->SetTranslation(TEXT("翻译后的文本"));
MyState->SetState(EOneSkyState::Finalized);
```

## Demo 示例

以下示例展示如何在编辑器工具代码中配置并检查 OneSky 连接状态：

```cpp
// MyOneSkyHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyOneSkyHelper
{
public:
    /** 初始化 OneSky 服务并测试连接 */
    static bool InitializeOneSkyService(const FString& InApiKey, const FString& InApiSecret);

    /** 为指定目标设置 OneSky 映射 */
    static void MapTargetToOneSkyProject(
        const FGuid& TargetGuid,
        int32 OneSkyProjectId,
        const FString& OneSkyFileName);

    /** 导出指定目标的所有文化版本到 OneSky */
    static bool ExportTargetToOneSky(TWeakObjectPtr<ULocalizationTarget> LocalizationTarget);
};
```

```cpp
// MyOneSkyHelper.cpp
#include "MyOneSkyHelper.h"
#include "OneSkyLocalizationServiceModule.h"
#include "OneSkyLocalizationServiceProvider.h"
#include "OneSkyLocalizationServiceSettings.h"

bool FMyOneSkyHelper::InitializeOneSkyService(
    const FString& InApiKey, const FString& InApiSecret)
{
    // 检查模块是否已加载
    if (!FModuleManager::Get().IsModuleLoaded("OneSkyLocalizationService"))
    {
        UE_LOG(LogTemp, Warning, TEXT("OneSkyLocalizationService 模块未加载"));
        return false;
    }

    FOneSkyLocalizationServiceModule& Module = FOneSkyLocalizationServiceModule::Get();

    // 配置凭据
    FOneSkyLocalizationServiceSettings& Settings = Module.AccessSettings();
    Settings.SetApiKey(InApiKey);
    Settings.SetApiSecret(InApiSecret);
    Settings.SetSaveSecretKey(true);
    Settings.SaveSettings();

    // 尝试建立连接
    FOneSkyLocalizationServiceProvider& Provider = Module.GetProvider();
    bool bConnected = Provider.EstablishPersistentConnection();

    UE_LOG(LogTemp, Log, TEXT("OneSky 连接状态: %s"),
        bConnected ? TEXT("成功") : TEXT("失败"));

    return bConnected;
}

void FMyOneSkyHelper::MapTargetToOneSkyProject(
    const FGuid& TargetGuid,
    int32 OneSkyProjectId,
    const FString& OneSkyFileName)
{
    FOneSkyLocalizationServiceModule& Module = FOneSkyLocalizationServiceModule::Get();
    FOneSkyLocalizationServiceSettings& Settings = Module.AccessSettings();

    Settings.SetSettingsForTarget(TargetGuid, OneSkyProjectId, OneSkyFileName);
    Settings.SaveSettings();
}

bool FMyOneSkyHelper::ExportTargetToOneSky(
    TWeakObjectPtr<ULocalizationTarget> LocalizationTarget)
{
    if (!LocalizationTarget.IsValid())
    {
        return false;
    }

    FOneSkyLocalizationServiceModule& Module = FOneSkyLocalizationServiceModule::Get();
    FOneSkyLocalizationServiceProvider& Provider = Module.GetProvider();

    // 检查服务器是否可用
    if (!Provider.IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("OneSky 服务不可用"));
        return false;
    }

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Localization` | 本地化服务框架接口（ILocalizationServiceProvider 等） |
| `HTTP` | 与 OneSky REST API 进行 HTTP 通信（IHttpRequest/IHttpResponse） |
| `Json` | 解析 OneSky API 的 JSON 响应数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 截断到 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 UE_LOGF |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复不可达代码的编译警告 |
| 2023-10-12 | `ffb133e7` | Update more code using FJsonObject to use TCHAR strings instead of ANSI strings. | FJsonObject 从 ANSI 字符串迁移到 TCHAR 字符串 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的批量提交 |

### 维护评价

**⚠️ 可能已废弃 / 不建议用于生产环境**

- **创建于 2015 年**，距今已超过 10 年，是引擎中最老的插件之一
- **从未完成初始开发**：首条 commit 明确指出"接口尚未实现完毕，仍有调试代码残留"。后续 10 年的 commit 全部为引擎范围的机械性重构（日志宏迁移、ANSI→TCHAR、编译警告修复），**零功能更新**
- **Beta 标记从未移除**：`IsBetaVersion=true` 且 `EnabledByDefault=false`，说明 Epic 从未认为它达到可发布状态
- **OneSky API 可能已过时**：源码中引用的 OneSky API 文档路径（`github.com/onesky/api-documentation-platform`）和项目结构可能与当前 OneSky 平台不兼容
- **测试用例缺失**：无自动化测试覆盖
- **结论**：这是一个被放弃的实验性插件。如果需要 OneSky 集成，建议使用 OneSky 官方 API 自行实现，或寻找社区维护的替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/OneSkyLocalizationService)
- [官方文档]()（无）