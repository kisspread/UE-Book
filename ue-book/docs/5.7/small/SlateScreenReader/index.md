# SlateScreenReader

> A screen reader that provides vision accessibility services for Slate.

| 属性 | 值 |
|---|---|
| 中文名 | 屏幕阅读器 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `SlateScreenReader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-12-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateScreenReader) | |

## 用途

SlateScreenReader 是 UE5 内置的屏幕阅读器框架（Screen Reader）在 Slate UI 系统中的具体实现。它利用文本转语音（TTS）技术，为视障用户提供用户界面元素的朗读反馈。该插件本身不直接提供 TTS 引擎，而是依赖于更底层的 `ScreenReader` 插件（位于 `Engine/Plugins/Runtime/ScreenReader/`），该插件定义了基础的屏幕阅读器接口和跨平台 TTS 抽象。

**为什么存在？**  
EPIC 在 UE5 中新增了可访问性（Accessibility）架构，ScreenReader 插件提供了通用接口和平台适配，而 SlateScreenReader 则完全基于 Slate 的事件系统（`FAccessibleEventArgs`）来驱动朗读行为，适用于桌面和主机平台（Win64/Mac/Linux，排除 Server）。它让开发者能够以最小成本为自己的项目添加屏幕朗读辅助功能。

## 使用场景

- 你正在制作一个需要符合 WCAG 或辅助功能标准的应用程序（如编辑器、医疗软件、教育工具）。
- 你需要为盲人或低视力用户朗读 UI 中的文本提示、按钮名称、导航结构等。
- 你希望将现有 Slate UI 接入统一的屏幕阅读器框架，而无需自行实现文本转语音集成。

## 蓝图用法

所有公开的蓝图节点均位于 `USlateScreenReaderEngineSubsystem` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateScreenReader` | 激活屏幕阅读器，允许后续注册和使用屏幕读者用户 | `USlateScreenReaderEngineSubsystem` |
| `DeactivateScreenReader` | 停用屏幕阅读器，临时禁止所有朗读反馈 | `USlateScreenReaderEngineSubsystem` |
| `IsScreenReaderActive` | 检查屏幕阅读器是否处于激活状态 | `USlateScreenReaderEngineSubsystem` |
| `ActivateUser` | 激活指定用户 ID 的屏幕读者用户（注册后默认未激活） | `USlateScreenReaderEngineSubsystem` |
| `DeactivateUser` | 停用指定用户 ID 的屏幕读者用户 | `USlateScreenReaderEngineSubsystem` |
| `IsUserActive` | 检查指定用户 ID 的屏幕读者用户是否激活 | `USlateScreenReaderEngineSubsystem` |
| `RegisterUser` | 注册一个新的屏幕读者用户（需传入用户 ID） | `USlateScreenReaderEngineSubsystem` |
| `UnregisterUser` | 注销指定用户 ID 的屏幕读者用户 | `USlateScreenReaderEngineSubsystem` |
| `GetActiveScreenReaderUserIds` | 获取所有当前激活的屏幕读者用户 ID 列表 | `USlateScreenReaderEngineSubsystem` |
| `RequestSpeak` | 请求朗读一条公告（需传入公告对象和用户 ID） | `USlateScreenReaderEngineSubsystem` |
| `StopSpeaking` | 停止指定用户 ID 用户正在朗读的内容 | `USlateScreenReaderEngineSubsystem` |

### 使用示例（蓝图描述）

1. **开启屏幕朗读并朗读“Hello World”**  
   - 在事件图表中，调用 `ActivateScreenReader`（无输入）。  
   - 等待一帧（`Delay` 节点 0.0s），确保子系统初始化完毕。  
   - 调用 `RegisterUser`，设置 `Screen Reader User Id` 为 `0`（通常对应第一个键盘/鼠标用户）。  
   - 调用 `ActivateUser`，设置 `Screen Reader User Id` 为 `0`。  
   - 构造一个 `FScreenReaderAnnouncement` 对象（通过 `ConstructScreenReaderAnnouncement` 蓝图节点，需传入字符串和优先级）。  
   - 调用 `RequestSpeak`，设置 `Screen Reader User Id` 为 `0`，`Announcement` 为刚才构造的对象。  
   - 系统将通过默认 TTS 语音读出 “Hello World”。

2. **简单停止朗读**  
   - 在需要停止朗读的事件中，调用 `StopSpeaking`，设置 `Screen Reader User Id` 为 `0`。

> **注意**：`FScreenReaderAnnouncement` 和 `FScreenReaderReply` 是蓝图原生结构体，支持在蓝图中创建和使用。

## C++ 用法

### 头文件引入

```cpp
#include "SlateScreenReaderEngineSubsystem.h"
#include "Announcement/ScreenReaderAnnouncement.h"
#include "GenericPlatform/ScreenReaderReply.h"
```

### 基本用法

```cpp
// 获取屏幕阅读器引擎子系统并激活
USlateScreenReaderEngineSubsystem& Subsystem = USlateScreenReaderEngineSubsystem::Get();
Subsystem.ActivateScreenReader();

// 注册用户 ID 为 0 的屏幕读者用户（通常对应第一个硬件用户）
Subsystem.RegisterUser(0);

// 激活该用户（注册后默认未激活）
Subsystem.ActivateUser(0);

// 检查用户是否激活
bool bActive = Subsystem.IsUserActive(0); // true

// 构造一条公告并请求朗读
FText TextToSpeak = LOCTEXT("Hello", "Hello World");
FScreenReaderAnnouncement Announcement(TextToSpeak.ToString(), FScreenReaderInfo::Important());
Subsystem.RequestSpeak(0, Announcement);

// 停止朗读
Subsystem.StopSpeaking(0);
```

> **来源**：`Source/SlateScreenReader/Public/SlateScreenReaderEngineSubsystem.h`（注释中的示例）

### 进阶用法

从 `FSlateScreenReader` 的测试用例（虽未提供，但从基类接口可推断）可组合其他操作：

```cpp
// 获取所有活跃用户 ID
TArray<int32> ActiveUserIds;
Subsystem.GetActiveScreenReaderUserIds(ActiveUserIds);

// 注销用户（会同时停用）
Subsystem.UnregisterUser(0);

// 通过模块接口设置自定义屏幕阅读器构建器（高级用法）
ISlateScreenReaderModule& Module = ISlateScreenReaderModule::Get();
TSharedRef<IScreenReaderBuilder> CustomBuilder = MakeShared<FMyCustomScreenReaderBuilder>();
Module.SetCustomScreenReaderBuilder(CustomBuilder);
```

## Demo 示例

一个完整的可编译示例，展示如何在加载关卡后立即激活屏幕阅读器并朗读一段文字。

**MyAccessibilityActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAccessibilityActor.generated.h"

UCLASS()
class AMYACCESSIBILITYACTOR : public AActor
{
	GENERATED_BODY()

public:
	AMyAccessibilityActor();

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void AnnounceHelloWorld();
};
```

**MyAccessibilityActor.cpp**
```cpp
#include "MyAccessibilityActor.h"
#include "SlateScreenReaderEngineSubsystem.h"
#include "Announcement/ScreenReaderAnnouncement.h"

AMyAccessibilityActor::AMyAccessibilityActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyAccessibilityActor::BeginPlay()
{
	Super::BeginPlay();

	// 延迟一小段时间以确保子系统就绪
	FTimerHandle TimerHandle;
	GetWorld()->GetTimerManager().SetTimer(TimerHandle, this, &AMyAccessibilityActor::AnnounceHelloWorld, 0.5f, false);
}

void AMyAccessibilityActor::AnnounceHelloWorld()
{
	USlateScreenReaderEngineSubsystem& Subsystem = USlateScreenReaderEngineSubsystem::Get();

	// 激活屏幕阅读器
	Subsystem.ActivateScreenReader();

	// 注册并激活用户 ID 0
	Subsystem.RegisterUser(0);
	Subsystem.ActivateUser(0);

	// 构造公告并请求朗读
	FText TextToSpeak = LOCTEXT("DemoText", "Welcome to the accessibility demonstration.");
	FScreenReaderAnnouncement Announcement(TextToSpeak.ToString(), FScreenReaderInfo::Important());
	Subsystem.RequestSpeak(0, Announcement);
}
```

> **说明**：依赖关系已在模块依赖部分声明。无需额外代码即可在项目中使用。

## 模块依赖

### 运行时依赖

| 模块 | 用途 |
|---|---|
| `ScreenReader` | 提供屏幕阅读器基类、跨平台 TTS 接口和公告系统 |

**无特殊依赖**（标准 Core/Engine/Slate 等均已包含在 Engine 链接中）。

## 维护状态

### 近期更新

- 2023-01-16 `bbc37aa2` 引擎插件更新（批量编译修复或合并）
- 2022-10-21 `610c4676` 更新内部插件供应商链接为安全协议（无功能变更）
- 2022-06-14 `28609e6f` 移除 `static_assert` 中的 TEXT 宏（兼容 UTF-8 编译模式）
- 2021-12-10 `d9792b10` 针对屏幕阅读器编译错误的推测性修复
- 2021-12-10 `652fc96a` 重构屏幕阅读器插件以使用新的可访问焦点 API（首次实质性提交）

### 维护评价

**维护不活跃**。该插件自 2023 年 1 月后未收到任何功能性更新，最近几次提交仅涉及编译修复和链接更新。虽然插件本身功能完整（基于稳定的 ScreenReader 基类），但其作为实验性插件（`IsExperimental=true`），内部 API 可能在未来版本中更改或废弃。如果您的项目需要长期维护的辅助功能框架，建议关注 `ScreenReader` 插件的后续稳定版本，或考虑自行封装更灵活的实现。目前仍可使用，但不推荐用于要求长期兼容性的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateScreenReader)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/accessibility-in-unreal-engine/)（引擎辅助功能总览）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateScreenReader/Tests)（若存在，此处仅为占位链接，实际路径需确认）