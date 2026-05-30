# Take Recorder Naming Tokens

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 录制命名令牌 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

---

> **本文档聚焦子模块 `TakeRecorderNamingTokens`**，该模块是 Takes 插件中负责命名令牌（Naming Tokens）扩展的部分。

## 用途

`TakeRecorderNamingTokens` 模块为 Take Recorder 提供**动态命名令牌**功能。在虚拟制片工作流中，每次录制的 Take 需要自动生成包含场景信息、板号、Take 编号等元数据的文件名和序列名称。该模块基于引擎的 NamingTokens 框架，注册一组以 `tr` 为命名空间的专用令牌（如 `{tr.take}`、`{tr.slate}` 等），使用户可以自定义 Take Recorder 录制资产的命名模板。

简单来说：**解决"录制时文件名怎么自动起"的问题**。用户在 Take Recorder 设置中配置命名模板，引擎在录制时自动替换令牌为实际的 Slate、Take 编号、时间戳等值。

## 使用场景

- 你在使用 Take Recorder 录制虚拟制片的多机位 Take → 需要自动按 `{tr.slate}_{tr.take}` 格式命名输出文件
- 你的后期管线要求特定命名规范 → 自定义命名模板使用 `tr` 命名空间的令牌
- 你需要在命名中包含录制时间戳 → 使用 `{tr.datetime}` 等时间相关令牌
- 多人协作需要统一命名规则 → 团队共享命名模板配置

## 蓝图用法

该模块主要提供底层命名令牌注册，本身不暴露大量蓝图节点。核心蓝图接口在上层 `TakeRecorder` 模块中。但开发者可以查询命名空间。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ITakeRecorderNamingTokensModule::GetTakeRecorderNamespace()` | 返回 Take Recorder 的令牌命名空间字符串 `"tr"` | `ITakeRecorderNamingTokensModule` |
| `UTakeRecorderNamingTokens::OnCreateDefaultTokens()` | 注册默认的 Take Recorder 命名令牌（内部调用） | `UTakeRecorderNamingTokens` |

### 使用示例（命名模板配置）

在 Take Recorder 面板中配置录制命名模板时，使用 `tr` 命名空间：

```
{tr.slate}_{tr.take}_{tr.datetime}
```

录制时自动解析为类似：`Shot01_003_20260526_143022` 的格式。

## C++ 用法

### 头文件引入

```cpp
#include "ITakeRecorderNamingTokensModule.h"
#include "TakeRecorderNamingTokens.h"
```

### 基本用法

获取 Take Recorder 的命名空间标识：

```cpp
// 获取 Take Recorder 使用的命名空间（返回 "tr"）
FString Namespace = ITakeRecorderNamingTokensModule::GetTakeRecorderNamespace();
// Namespace == TEXT("tr")
```

**来源**: `Public/ITakeRecorderNamingTokensModule.h`

### 进阶用法

如果你需要自定义扩展 Take Recorder 的命名令牌系统，可以继承 `UNamingTokens` 并注册自己的令牌类。参考 `UTakeRecorderNamingTokens` 的实现模式：

```cpp
// 继承 UNamingTokens 以创建自定义令牌集
UCLASS(NotBlueprintable)
class UMyCustomRecorderTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyCustomRecorderTokens();

protected:
    // 注册默认令牌
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override;

    // 求值前的准备工作（缓存上下文）
    virtual void OnPreEvaluate_Implementation(const FNamingTokensEvaluationData& InEvaluationData) override;

    // 求值后的清理工作
    virtual void OnPostEvaluate_Implementation() override;

    // 自定义时间获取（可用于时间偏移等场景）
    virtual FDateTime GetCurrentDateTime_Implementation() const override;
};
```

**来源**: `Private/TakeRecorderNamingTokens.h`

## Demo 示例

一个最小的自定义 Take Recorder 命名令牌扩展：

### MyCustomRecorderTokens.h

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "NamingTokens.h"
#include "MyCustomRecorderTokens.generated.h"

/**
 * 自定义 Take Recorder 命名令牌示例
 * 添加一个 {tr.location} 令牌表示拍摄地点
 */
UCLASS(NotBlueprintable)
class MYPROJECT_API UMyCustomRecorderTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyCustomRecorderTokens();

protected:
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override;
    virtual void OnPreEvaluate_Implementation(const FNamingTokensEvaluationData& InEvaluationData) override;
    virtual void OnPostEvaluate_Implementation() override;

private:
    /** 当前上下文中缓存的拍摄地点 */
    FString CachedLocation;
};
```

### MyCustomRecorderTokens.cpp

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyCustomRecorderTokens.h"

UMyCustomRecorderTokens::UMyCustomRecorderTokens()
{
    // 设置命名空间为 "tr"，与 Take Recorder 原生令牌共存
    Namespace = TEXT("tr");
}

void UMyCustomRecorderTokens::OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens)
{
    Super::OnCreateTokens(Tokens);

    // 注册自定义令牌 {tr.location}
    FNamingTokenData& LocationToken = Tokens.AddDefaulted_GetRef();
    LocationToken.Token = TEXT("location");
    LocationToken.DisplayName = NSLOCTEXT("MyCustomRecorderTokens", "LocationToken", "Location");
    LocationToken.Description = NSLOCTEXT("MyCustomRecorderTokens", "LocationTokenDesc", "The recording location");
    LocationToken.TokenDelegate = FNamingTokenData::FTokenDelegate::CreateLambda([this]() -> FString
    {
        return CachedLocation.IsEmpty() ? TEXT("Default") : CachedLocation;
    });
}

void UMyCustomRecorderTokens::OnPreEvaluate_Implementation(const FNamingTokensEvaluationData& InEvaluationData)
{
    Super::OnPreEvaluate_Implementation(InEvaluationData);
    // 从评估上下文中缓存所需数据
    CachedLocation = TEXT("Stage_A");
}

void UMyCustomRecorderTokens::OnPostEvaluate_Implementation()
{
    Super::OnPostEvaluate_Implementation();
    // 清理缓存
    CachedLocation.Reset();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 引擎级命名令牌框架，提供 `UNamingTokens` 基类 |
| `TakesCore` | Take 元数据核心（`UTakeMetaData` 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attachment | 修复 Attach Track Recorder 无法正确录制附着关系的回归问题 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 修复子 Section 序列为 null 时导致的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 为日志输出添加缺失的 WITH_EDITOR 编译保护 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复弱指针因类型转换触发断言导致的潜在崩溃 |

### 维护评价

Take Recorder 整体插件处于**活跃维护**状态。截至 2026 年 5 月仍有频繁的 bug 修复和回归问题修复提交。作为 Unreal Engine 虚拟制片（Virtual Production）工作流的核心组件之一，该插件受到 Epic Games 持续关注和维护。

`TakeRecorderNamingTokens` 子模块作为命名令牌扩展，功能稳定且代码量小（仅 3 个头文件），随主插件一并维护。**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)（无独立测试目录，测试位于主引擎测试套件中）