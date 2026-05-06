# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇幻彩设备 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画资源） |
| 模块 | `RazerChromaDevices` (ClientOnlyNoCommandlet), `RazerChromaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices) | |

## 用途

该插件使你的 UE5 项目能够与 **Razer Chroma** 外设生态系统交互，在运行时动态控制支持 Chroma 的设备（键盘、鼠标、耳机、鼠标垫、小键盘、Chroma Link 等）的灯光效果。它包装了 Razer Chroma SDK，提供基于蓝图和 C++ 的动画播放、灯光颜色设置、空闲动画管理等高级功能，无需手动加载 DLL 或处理原生 API。适用于需要沉浸式灯光反馈的游戏、工具或体验。

## 使用场景

- **游戏反馈**：根据游戏事件（掉血、击杀、技能冷却、连杀）改变设备灯光颜色或播放特定动画。
- **交互式体验**：在展览、VR 体验中，利用键盘或鼠标灯光引导用户操作。
- **品牌展示**：应用启动时播放品牌动画，或根据用户状态（空闲、忙碌）切换灯光模式。
- **调试/可视化**：在编辑器中将某些状态（如 AI 行为、网络延迟）映射到不同区域的灯光。

## 蓝图用法

所有蓝图可调用函数均位于 `URazerChromaFunctionLibrary` 中。该库是游戏逻辑与插件的核心交互入口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsChromaRuntimeAvailable` | 检查当前机器是否已安装 Razer Chroma 运行时（DLL 是否已加载）。 | `URazerChromaFunctionLibrary` |
| `PlayChromaAnimation` | 播放指定的 `.chroma` 动画资产，可选择是否循环。 | `URazerChromaFunctionLibrary` |
| `StopChromaAnimation` | 停止指定动画的播放。 | `URazerChromaFunctionLibrary` |
| `PauseChromaAnimation` | 暂停指定动画。 | `URazerChromaFunctionLibrary` |
| `ResumeChromaAnimation` | 恢复已暂停的动画，并可设置循环。 | `URazerChromaFunctionLibrary` |
| `IsAnimationPlaying` | 查询指定动画是否正在播放。 | `URazerChromaFunctionLibrary` |
| `IsChromaAnimationPaused` | 查询指定动画是否已暂停。 | `URazerChromaFunctionLibrary` |
| `StopAllChromaAnimations` | 立即停止所有正在播放的 Chroma 动画。 | `URazerChromaFunctionLibrary` |
| `SetIdleAnimation` | 设置一个空闲动画，当没有其他动画播放时自动循环播放。 | `URazerChromaFunctionLibrary` |
| `UseIdleAnimations` | 启用或禁用空闲动画功能。 | `URazerChromaFunctionLibrary` |
| `SetChromaLightColor` | 直接设置指定设备（如键盘、鼠标等）的整体静态颜色（使用 `FRazerChromaLightColorData` 结构）。 | `URazerChromaFunctionLibrary` |

> 注意：`FRazerChromaLightColorData` 和 `ERazerChromaDeviceTypes` 等结构可在蓝图中构造和读写。`FRazerChromaLightColorData` 包含 `DeviceType`（位掩码）和 `Color`。

### 使用示例（蓝图描述）

1. **播放循环动画**：
   - 获取 `URazerChromaAnimationAsset` 变量（已通过内容浏览器导入 `.chroma` 文件）。
   - 调用 `PlayChromaAnimation`，输入动画资产，`bLooping` 连接 `true`。
   - 返回的布尔值可用于判断是否播放成功。

2. **设置空闲动画**：
   - 在项目设置 → 插件 → Razer Chroma Devices 中配置默认空闲动画，或在运行时调用 `SetIdleAnimation` 并传入资产。
   - 调用 `UseIdleAnimations(true)` 启用空闲动画。

3. **切换设备颜色**：
   - 调用 `SetChromaLightColor`，从引脚构造 `FRazerChromaLightColorData`，将 `DeviceType` 设为 `ERazerChromaDeviceTypes::Keyboard`，`Color` 设为红色。
   - 可实现“受伤时键盘变红”等效果。

## C++ 用法

### 头文件引入

```cpp
#include "RazerChromaFunctionLibrary.h"
#include "RazerChromaAnimationAsset.h"
#include "RazerChromaDeviceProperties.h"  // 如需直接使用设备属性结构
```

### 基本用法

以下示例演示在游戏模式（示例类）中播放动画：

```cpp
// 假设你有 URazerChromaAnimationAsset* 的引用 MyAnimAsset
if (URazerChromaFunctionLibrary::IsChromaRuntimeAvailable())
{
    bool bSuccess = URazerChromaFunctionLibrary::PlayChromaAnimation(MyAnimAsset, true /* bLoop */);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to play Chroma animation"));
    }
}
```

### 进阶用法

**自定义设备属性（基于输入设备框架）**：

该插件实现了 `IInputDevice` 接口，支持通过 `SetDeviceProperty` 机制播放动画。通常直接使用函数库即可，但高级场景可使用 `FRazerChromaPlayAnimationFile` 属性：

```cpp
#include "InputCoreTypes.h"
#include "GenericPlatform/IInputInterface.h"  // 需要获取 IInputInterface

void YourClass::TriggerChromaEffect()
{
    if (IInputInterface* InputInterface = GetInputInterface())
    {
        FRazerChromaPlayAnimationFile Property;
        Property.AnimName = MyAnimAsset->GetAnimationName();   // 或直接使用函数库
        Property.AnimationByteBuffer = MyAnimAsset->GetAnimByteBuffer();
        Property.bLooping = false;

        // 应用到指定控制器和平台用户
        FInputDeviceId DeviceId = FInputDeviceId::CreateFromInternalId(0);
        InputInterface->SetDeviceProperty(DeviceId, &Property);
    }
}
```

**直接设置静态灯光颜色**：

```cpp
FRazerChromaLightColorData LightData;
LightData.DeviceType = static_cast<int32>(ERazerChromaDeviceTypes::Keyboard | ERazerChromaDeviceTypes::Mouse);
LightData.Color = FLinearColor::Red;

URazerChromaFunctionLibrary::SetChromaLightColor(LightData);
```

**管理空闲动画**：

```cpp
// 运行时切换空闲动画（需要先设置 UObject 路径或直接使用资产路径）
URazerChromaFunctionLibrary::SetIdleAnimation(IdleAnimAsset);
URazerChromaFunctionLibrary::UseIdleAnimations(true);
```

## Demo 示例

以下是一个最小 C++ 类，展示如何在游戏开始时播放一个 Razer Chroma 动画，并在退出时停止所有动画。

**ChromaDemoGameMode.h**:

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once
#include "GameFramework/GameModeBase.h"
#include "ChromaDemoGameMode.generated.h"

class URazerChromaAnimationAsset;

UCLASS()
class AChromaDemoGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AChromaDemoGameMode();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chroma")
    URazerChromaAnimationAsset* IntroAnimation;

private:
    void PlayIntroAnimation();
};
```

**ChromaDemoGameMode.cpp**:

```cpp
#include "ChromaDemoGameMode.h"
#include "RazerChromaFunctionLibrary.h"
#include "RazerChromaAnimationAsset.h"
#include "RazerChromaDeviceLogging.h"

AChromaDemoGameMode::AChromaDemoGameMode()
{
    // 可以在蓝图中设置 IntroAnimation
}

void AChromaDemoGameMode::BeginPlay()
{
    Super::BeginPlay();
    PlayIntroAnimation();
}

void AChromaDemoGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理所有动画
    if (URazerChromaFunctionLibrary::IsChromaRuntimeAvailable())
    {
        URazerChromaFunctionLibrary::StopAllChromaAnimations();
    }
    Super::EndPlay(EndPlayReason);
}

void AChromaDemoGameMode::PlayIntroAnimation()
{
    if (IntroAnimation && URazerChromaFunctionLibrary::IsChromaRuntimeAvailable())
    {
        bool bSuccess = URazerChromaFunctionLibrary::PlayChromaAnimation(IntroAnimation, false /* bLoop */);
        if (!bSuccess)
        {
            UE_LOG(LogRazerChroma, Warning, TEXT("Failed to play intro Chroma animation."));
        }
    }
}
```

**注意**：需要在游戏模块的 `Build.cs` 中添加 `RazerChromaDevices` 依赖（见模块依赖）。

## 模块依赖

要使用本插件（RazerChromaDevices 模块），你的模块需添加以下独特依赖：

| 模块 | 用途 |
|---|---|
| `RazerChromaSDK` | 提供原生 Razer Chroma SDK 类型定义和 DLL 加载（外部模块） |

> 无需列出 Core、Engine 等常见依赖。

## 维护状态

### 近期更新

- 2025-07-10  `9803c443` 为对应 .gen.cpp 的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME（代码生成一致性）
- 2025-06-26  `ec900998` 同上（可能跨不同源文件）
- 2025-06-10  `570dd339` 移动 RazerChromaEditor 的 Private 目录以符合标准模块布局
- 2025-05-29  `1b731fe6` 禁用 Windows Arm64 平台的 RazerChromaDevices 模块
- 2025-05-23  `13b6ed9e` 移除 win32 情况（早期适配）

### 维护评价

- **创建时间**：2025 年 5 月（约 2 个月前的全新插件）
- **更新频率**：至少每 2～3 周有提交，活跃度较高
- **当前状态**：`IsBetaVersion=true`，且 `EnabledByDefault=false`，表明仍处于实验阶段，API 可能变化。默认关闭需要在项目设置中手动启用。
- **已知限制**：仅支持 Windows（Arm64 已被禁用）；需要用户已安装 Razer Synapse 及 Chroma SDK；动画文件为专用 `.chroma` 格式，需通过编辑器导入。
- **推荐使用**：对于希望集成 Razer Chroma 灯效的新项目，可以试用；但应注意其实验性质，产品发布前需充分测试。建议配合项目设置中的空闲动画和设备类型位掩码进行配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices)
- [官方文档（Razer Chroma SDK）](https://developer.razer.com/chroma/)
- [测试用例（如有）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RazerChromaDevices/Tests)（本插件未提供独立测试目录）