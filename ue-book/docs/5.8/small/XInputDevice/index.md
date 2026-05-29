# XInput Device

> XInput is a Game Controller API for Windows.

| 属性 | 值 |
|---|---|
| 中文名 | XInput 游戏控制器 |
| 分类 | Input Devices |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `XInputDevice` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-08-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/XInputDevice) | |

## 用途

这个插件将 Windows 平台上的 XInput 游戏控制器支持从引擎的核心 WindowsApplication 模块中分离出来，成为独立的插件模块。

**核心作用**：
1. **模块化重构**：将原本内嵌于 `WindowsApplication.cpp` 中的 XInput 逻辑抽离，使其成为可选组件。
2. **为 GameInput 铺路**：通过模块化，未来可以轻松地将默认输入设备切换为更现代的 GameInput API，而无需修改核心代码。
3. **简化开关控制**：开发者现在可以通过插件系统简单地启用或禁用 XInput 支持，避免了在引擎源码中添加大量条件检查。

## 使用场景

- 你在开发一个 **Windows 平台的 PC 游戏**，需要支持 Xbox 控制器（XInput 兼容设备）。
- 你想在不重新编译引擎的情况下，**启用或禁用 XInput 支持**。
- 你正在测试 **GameInput API**，并希望暂时禁用 XInput 以避免冲突。
- 你之前为了扩展 XInput 功能而修改了引擎源码，现在需要**迁移到模块化结构**。

## 蓝图用法

此插件主要通过引擎的输入系统（`IInputDevice` 接口）工作，不直接暴露新的蓝图节点。控制器的状态（摇杆、扳机、按键）会通过标准的输入事件系统传递给游戏。

### 核心机制

游戏通过以下标准方式接收 XInput 数据：

1. **轴输入 (Axis Inputs)**：
   - `Gamepad Left X` / `Gamepad Left Y`：左摇杆轴
   - `Gamepad Right X` / `Gamepad Right Y`：右摇杆轴
   - `Gamepad Left Trigger Axis` / `Gamepad Right Trigger Axis`：扳机轴

2. **按键输入 (Button Inputs)**：
   - 所有 Xbox 风格的按键（`Gamepad FaceButton Bottom`， `Gamepad FaceButton Right` 等）。

3. **力反馈 (Force Feedback)**：
   - 通过 `FForceFeedbackValues` 和 `SetChannelValue`/`SetChannelValues` 控制手柄震动。

### 使用示例（蓝图描述）

在蓝图中，你无需直接与 `XInputDevice` 交互。在项目设置 -> 输入中，映射到 `Gamepad` 类别下的按键和轴即可。例如：
- 将 `Action: Fire` 映射到 `Gamepad Right Trigger`
- 将 `Axis: MoveForward` 映射到 `Gamepad Left Y`

## C++ 用法

### 头文件引入

由于 `XInputInterface.h` 原本是私有头文件，此插件重构后将其移至模块内部，外部代码通常不应直接包含它。标准用法是依赖引擎的 `IInputDeviceModule` 接口。

```cpp
#include "InputDeviceModule.h" // IInputDeviceModule 的基类
```

### 基本用法

此插件的核心是实现 `IInputDeviceModule` 接口，为引擎提供 `XInputInterface` 设备。外部代码通常不直接实例化它，而是由引擎在启动时根据插件配置自动创建。

```cpp
// 以下代码展示了插件模块如何向引擎注册自己，这是插件内部的工作方式。
// 来自：Source/XInputDevice/Public/XInputDeviceModule.h

class FXInputDeviceModule final : public IInputDeviceModule
{
public:
    // 当引擎请求创建输入设备时，返回一个 XInputInterface 实例
    virtual TSharedPtr<IInputDevice> CreateInputDevice(const TSharedRef<FGenericApplicationMessageHandler>& InMessageHandler) override;
    
    // 带参数的版本，用于特定场景
    virtual TSharedPtr<IInputDevice> CreateInputDevice(const TSharedRef<FGenericApplicationMessageHandler>& InMessageHandler, FInputDeviceCreationParameters InParameters) override;
    
    // 返回此设备偏好的 API 字符串标识
    virtual const TCHAR* GetPreferredDeviceAPIString() const override;
};
```

### 进阶用法

如果你需要直接与 `XInputInterface` 交互（例如，查询手柄连接状态），可以获取当前活动的输入设备接口。

```cpp
#include "GenericPlatform/ITextInputMethodSystem.h"
#include "InputDevice.h"

// 获取当前平台的主输入设备（可能是 XInputInterface）
TSharedPtr<IInputDevice> InputDevice = FSlateApplication::Get().GetPlatformApplication()->GetInputDevice();

// 检查是否有手柄连接
if (InputDevice.IsValid())
{
    bool bGamepadAttached = InputDevice->IsGamepadAttached();
    UE_LOG(LogTemp, Log, TEXT("Gamepad attached: %s"), bGamepadAttached ? TEXT("true") : TEXT("false"));
}

// 直接设置力反馈（如果知道是 XInput 设备）
if (TSharedPtr<XInputInterface> XInputDevice = StaticCastSharedPtr<XInputInterface>(InputDevice))
{
    // 设置 0 号控制器的马达震动强度
    FForceFeedbackValues ForceValues;
    ForceValues.LeftLarge = 0.5f;  // 左侧大马达，强度0.5
    ForceValues.RightSmall = 0.8f; // 右侧小马达，强度0.8
    XInputDevice->SetChannelValues(0, ForceValues);
}
```

## Demo 示例

这是一个最小的 C++ 示例，演示如何检查游戏手柄是否通过 XInput 连接。

### XInputDemoComponent.h

```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "XInputDemoComponent.generated.h"

UCLASS(ClassGroup=(Input), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UXInputDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UXInputDemoComponent();

protected:
    virtual void BeginPlay() override;

public:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    bool bWasGamepadAttached;
};
```

### XInputDemoComponent.cpp

```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#include "XInputDemoComponent.h"
#include "GenericPlatform/IInputInterface.h"
#include "Framework/Application/SlateApplication.h"

UXInputDemoComponent::UXInputDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    bWasGamepadAttached = false;
}

void UXInputDemoComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UXInputDemoComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 检查 Slate 应用程序和输入设备是否有效
    if (FSlateApplication::IsInitialized())
    {
        const TSharedPtr<GenericApplication> PlatformApp = FSlateApplication::Get().GetPlatformApplication();
        if (PlatformApp.IsValid())
        {
            TSharedPtr<IInputDevice> InputDevice = PlatformApp->GetInputDevice();
            if (InputDevice.IsValid())
            {
                bool bGamepadAttached = InputDevice->IsGamepadAttached();
                
                // 仅在状态改变时输出日志
                if (bGamepadAttached != bWasGamepadAttached)
                {
                    bWasGamepadAttached = bGamepadAttached;
                    UE_LOG(LogTemp, Log, TEXT("XInput Gamepad connection status changed: %s"), 
                           bGamepadAttached ? TEXT("Connected") : TEXT("Disconnected"));
                }
            }
        }
    }
}
```

## 模块依赖

从 `XInputDevice.build.cs` 分析，此插件模块仅依赖于标准引擎模块，没有独特的外部依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 此模块主要依赖引擎核心输入系统和平台抽象层 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式，保持代码库一致性。 |
| 2026-04-01 | `1afb0871` | [Input] Add a thread affinitiy for input for IInputDevice so that we can specify which input modules | 为 IInputDevice 添加线程亲和性支持，允许指定输入模块在哪个线程运行。 |
| 2026-03-31 | `b2cdd0a7` | [Xinput] add a comment to easily disable optimization in the XInput build module | 在 XInput 构建模块中添加注释，方便禁用优化。 |
| 2026-03-26 | `2cdca0c0` | [Input] FInputDeviceScope refactor and deprecation. | 重构并废弃 FInputDeviceScope，优化输入设备作用域管理。 |
| 2026-03-23 | `b22ef9f5` | [Input] Add a new FInputDeviceRegistry: | 添加新的 FInputDeviceRegistry，用于集中管理输入设备注册。 |

### 维护评价

- **创建时间**：2023年8月，相对较新的插件。
- **更新频率**：近期（2026年3-4月）有持续的更新，主要围绕输入系统的架构改进和代码维护。
- **维护活跃度**：**活跃维护中**。作为引擎输入系统模块化重构的一部分，受到 Epic 官方的关注。
- **已知问题/限制**：
  - 仅支持 Windows 平台（Win64）。
  - 其 `SupportedPrograms` 仅限于 `LiveLinkHub`，表明可能主要用于特定程序（如 Live Link Hub），而非通用游戏运行时。这可能是该模块的特殊用途限制。
- **推荐使用**：如果你需要在 Windows 上为 LiveLinkHub 程序使用 XInput 控制器，此插件是必需的。对于通用游戏开发，由于其 `SupportedPrograms` 限制，可能需要进一步确认其适用性。

**警告**：此插件的 `SupportedPrograms` 字段仅列出了 `LiveLinkHub`，这可能意味着它并非设计用于所有 UE 应用程序。在通用游戏项目中启用前，建议进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/XInputDevice)
- [官方文档](https://docs.unrealengine.com)（暂无专门页面，属于引擎输入系统的一部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime)（可能位于通用运行时测试中）