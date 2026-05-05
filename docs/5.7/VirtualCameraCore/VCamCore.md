# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、UMG 控件） |
| 模块 | `VCamCore` (Runtime), `VCamCoreEditor` (Runtime), `VCamBlueprintNodes` (Runtime), `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

VirtualCameraCore 是 Unreal Engine 虚拟制片（Virtual Production）管线的核心运行时框架。它解决的核心问题是：**如何通过外部物理设备（iPad、手机、专用硬件）实时控制引擎内的电影摄像机，并将摄像机画面流式传输回设备**。

该插件提供了一套完整的架构：

- **VCamComponent**：附加到 CineCameraActor 上的核心组件，管理修改器栈（Modifier Stack）、输出提供者（Output Provider）和输入处理
- **Modifier 系统**：可扩展的摄像机效果修改器，支持蓝图实现和 C++ 实现，通过 Connection Point 机制与 UI 控件通信
- **Output Provider 系统**：多种输出方式（视口覆盖、媒体输出、Pixel Streaming、Remote Session），将摄像机画面流式传输到外部设备
- **Input 系统**：基于 Enhanced Input 的输入处理，支持设备过滤、输入配置文件切换、输入消费策略
- **UI Widget 系统**：VCamWidget 基类提供 Connection 机制，让 UI 控件自动连接到 Modifier 的连接点，实现双向数据绑定

该插件是 `VirtualCamera` 内容插件的代码基础，后者提供实际的蓝图资产和 UI 模板。

## 使用场景

- 你在做虚拟制片项目，需要用 iPad 作为虚拟摄像机控制器 → 使用 VCamComponent + Remote Session Output
- 你需要将虚拟摄像机画面通过 Pixel Streaming 发送给远程导演 → 使用 PixelStreamingVCam 模块
- 你要自定义摄像机控制逻辑（如摇臂模拟、轨道运动）→ 继承 UVCamBlueprintModifier 实现自定义修改器
- 你需要在虚拟摄像机 UI 上显示自定义控件并绑定到摄像机参数 → 使用 UVCamWidget + Connection 机制
- 你要管理多个虚拟摄像机的输入设备分配 → 使用 FVCamInputDeviceConfig 进行设备过滤
- 你需要在多用户环境下同步虚拟摄像机状态 → 使用 VCamMultiUser 功能

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetVCamComponent` | 获取 Actor 上的 VCamComponent | `AVCamBaseActor` |
| `SetCurrentState` | 切换状态切换器的状态，触发连接重绑定 | `UVCamStateSwitcherWidget` |
| `GetCurrentState` | 获取当前状态名称 | `UVCamStateSwitcherWidget` |
| `GetStates` | 获取所有可用状态列表 | `UVCamStateSwitcherWidget` |
| `InitializeConnections` | 初始化控件与 Modifier 的连接 | `UVCamWidget` |
| `ReinitializeConnections` | 重新初始化所有连接 | `UVCamWidget` |
| `SetEnabled` | 启用/禁用修改器 | `UVCamModifier` |
| `IsEnabled` | 查询修改器是否启用 | `UVCamModifier` |
| `SetStackEntryName` | 设置修改器在栈中的名称 | `UVCamModifier` |
| `GetStackEntryName` | 获取修改器在栈中的名称 | `UVCamModifier` |
| `GetOwningVCamComponent` | 获取拥有此修改器的 VCamComponent | `UVCamModifier` |
| `GetCurrentLiveLinkDataFromOwningComponent` | 从所属组件获取 LiveLink 数据 | `UVCamModifier` |
| `AddCanActivateOutputProviderDelegate` | 添加输出提供者激活判断委托 | `UVCamCoreScriptingFunctionLibrary` |
| `RemoveCanActivateOutputProviderDelegate` | 移除激活判断委托 | `UVCamCoreScriptingFunctionLibrary` |
| `PromptClientForString` | 向 VCam 客户端发送字符串输入请求（异步） | `UPromptClientForStringAsyncAction` |
| `GetVCamInputSettings` | 获取输入设置单例 | `UVCamInputSettings` |
| `SetDefaultInputProfile` | 设置默认输入配置文件 | `UVCamInputSettings` |
| `SetInputProfiles` | 更新输入配置文件列表 | `UVCamInputSettings` |
| `GetInputProfileNames` | 获取所有配置文件名称 | `UVCamInputSettings` |

### 连接查询节点（VCamUIFunctionLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsConnected_VCamConnection` | 检查连接是否成功建立 | `UVCamUIFunctionLibrary` |
| `GetConnectionPointName_VCamConnection` | 获取连接点名称 | `UVCamUIFunctionLibrary` |
| `GetConnectedModifier_VCamConnection` | 获取已连接的 Modifier | `UVCamUIFunctionLibrary` |
| `GetConnectedInputAction_VCamConnection` | 获取关联的输入动作 | `UVCamUIFunctionLibrary` |
| `GetConnectionByName_VCamWidget` | 按名称获取 Widget 上的连接 | `UVCamUIFunctionLibrary` |
| `IsConnected_VCamWidget` | 检查 Widget 上指定连接是否已连接 | `UVCamUIFunctionLibrary` |
| `GetConnectedModifier_VCamWidget` | 获取 Widget 上指定连接的 Modifier | `UVCamUIFunctionLibrary` |

### 使用示例（蓝图描述）

**创建自定义虚拟摄像机修改器**：
1. 创建一个继承 `UVCamBlueprintModifier` 的蓝图类
2. 在 `ConnectionPoints` 中添加连接点（如 "FocusDistance"、"Aperture"）
3. 实现 `OnApply` 事件，接收 `CameraComponent` 和 `DeltaTime`，修改摄像机参数
4. 在 VCamComponent 的 Modifier Stack 中添加此修改器实例

**连接 UI 控件到修改器**：
1. 创建继承 `UVCamWidget` 的 UMG 控件
2. 在 `Connections` Map 中添加连接（如 "FocusConnection"）
3. 设置连接的 `RequiredInterfaces` 和 `bRequiresInputAction`
4. 将控件添加到 Output Provider 的 Overlay Widget 中
5. 当 Output Provider 激活时，连接会自动初始化
6. 实现 `OnConnectionUpdated` 事件处理连接结果

**使用状态切换器**：
1. 创建 `UVCamStateSwitcherWidget` 子类
2. 在 `States` 中定义多个状态（如 "Default"、"CloseUp"、"WideShot"）
3. 为每个状态配置 `WidgetConfigs`，指定哪些子控件的连接应重绑定到哪些 Modifier/ConnectionPoint
4. 调用 `SetCurrentState("CloseUp")` 切换状态，所有相关控件的连接自动更新

## C++ 用法

### 头文件引入

```cpp
#include "VCamComponent.h"
#include "VCamModifier.h"
#include "Output/VCamOutputProviderBase.h"
#include "UI/VCamWidget.h"
#include "Input/VCamInputSettings.h"
```

### 基本用法：创建自定义 Modifier

```cpp
// MyCameraModifier.h
#pragma once

#include "Modifier/VCamModifier.h"
#include "MyCameraModifier.generated.h"

UCLASS(Blueprintable, EditInlineNew)
class MYPROJECT_API UMyCameraModifier : public UVCamModifier
{
    GENERATED_BODY()
public:

    // 定义连接点，UI 控件可以通过 Connection 机制绑定到此
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    TMap<FName, FVCamModifierConnectionPoint> ConnectionPoints;

    // 每帧调用，修改摄像机参数
    virtual void Apply(UVCamModifierContext* Context, UCineCameraComponent* CameraComponent, const float DeltaTime) override
    {
        if (!CameraComponent) return;

        // 修改焦距
        CameraComponent->CurrentFocalLength = FMath::FInterpTo(
            CameraComponent->CurrentFocalLength,
            TargetFocalLength,
            DeltaTime,
            InterpSpeed
        );
    }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
    float TargetFocalLength = 50.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
    float InterpSpeed = 5.0f;
};
```

### 基本用法：输入配置

```cpp
// 配置 VCam 输入设备过滤
FVCamInputDeviceConfig InputConfig;
InputConfig.bAllowAllInputDevices = false;
InputConfig.AllowedInputDeviceIds.Add(FVCamInputDeviceID{ 0 }); // 只允许设备 ID 0

// 设置输入模式
InputConfig.InputMode = EVCamInputMode::ConsumeDevice;

// 应用到 VCamComponent 的输入子系统
UInputVCamSubsystem* InputSubsystem = VCamComponent->GetSubsystem<UInputVCamSubsystem>();
InputSubsystem->SetInputSettings(InputConfig);
```

### 进阶用法：自定义输出提供者

```cpp
// MyCustomOutputProvider.h
#pragma once

#include "Output/VCamOutputProviderBase.h"
#include "MyCustomOutputProvider.generated.h"

UCLASS(meta = (DisplayName = "Custom Output Provider"))
class UMyCustomOutputProvider : public UVCamOutputProviderBase
{
    GENERATED_BODY()
public:

    UMyCustomOutputProvider();

    virtual void OnActivate() override
    {
        Super::OnActivate();
        // 启动自定义输出流
        StartCustomStream();
    }

    virtual void OnDeactivate() override
    {
        StopCustomStream();
        Super::OnDeactivate();
    }

    virtual void Tick(const float DeltaTime) override
    {
        Super::Tick(DeltaTime);
        // 更新输出
    }

    // 自定义输出是否需要强制锁定视口
    virtual bool NeedsForceLockToViewport() const override { return true; }

    // 处理客户端字符串输入请求
    virtual TFuture<FVCamStringPromptResponse> PromptClientForString(const FVCamStringPromptRequest& Request) override
    {
        // 实现自定义的客户端输入提示
        auto Promise = TPromise<FVCamStringPromptResponse>();
        // ... 异步处理
        return Promise.GetFuture();
    }

private:
    void StartCustomStream();
    void StopCustomStream();
};
```

### 进阶用法：自定义 ViewTarget 策略

```cpp
// 自定义视图目标策略：选择特定的玩家控制器
UCLASS()
class UMyViewTargetPolicy : public UGameplayViewTargetPolicy
{
    GENERATED_BODY()
public:

    virtual TArray<APlayerController*> DeterminePlayerControllers_Implementation(
        const FDeterminePlayerControllersTargetPolicyParams& Params) override
    {
        TArray<APlayerController*> Result;
        // 自定义逻辑：选择特定的玩家控制器
        if (APlayerController* PC = GetSpecificPlayerController())
        {
            Result.Add(PC);
        }
        return Result;
    }

    virtual void UpdateViewTarget_Implementation(const FUpdateViewTargetPolicyParams& Params) override
    {
        // 自定义视图目标更新逻辑，例如带混合的切换
        for (APlayerController* PC : Params.PlayerControllers)
        {
            if (PC && Params.CameraToAffect)
            {
                PC->SetViewTarget(Params.CameraToAffect->GetOwner());
            }
        }
    }
};
```

### 进阶用法：管理输出提供者激活

```cpp
// 通过模块接口注册激活判断委托
IVCamCoreModule& Module = IVCamCoreModule::Get();
FUnifiedActivationDelegateContainer& Container = Module.OnCanActivateOutputProvider();

FDelegateHandle Handle = Container.Add(
    FUnifiedActivationDelegate(
        FCanChangeActiviationVCamDelegate::CreateLambda(
            [](const FVCamCoreChangeActivationArgs& Args) -> FVCamCoreChangeActivationResult
            {
                // 自定义激活条件判断
                if (Args.OutputProvider && ShouldBlockActivation(Args.OutputProvider))
                {
                    return { false, FText::FromString(TEXT("当前状态不允许激活")) };
                }
                return { true, FText::GetEmpty() };
            }
        )
    )
);

// 移除委托
Container.Remove(Handle);
```

## Demo 示例

### 自定义蓝图修改器（C++ 基类）

```cpp
// SimpleDollyModifier.h
#pragma once

#include "Modifier/VCamModifier.h"
#include "SimpleDollyModifier.generated.h"

UCLASS(Blueprintable, EditInlineNew, meta = (DisplayName = "Simple Dolly Modifier"))
class MYPROJECT_API USimpleDollyModifier : public UVCamModifier
{
    GENERATED_BODY()
public:

    USimpleDollyModifier();

    virtual void Initialize(UVCamModifierContext* Context, UInputComponent* InputComponent = nullptr) override;
    virtual void Apply(UVCamModifierContext* Context, UCineCameraComponent* CameraComponent, const float DeltaTime) override;

    /** 推拉速度（厘米/秒） */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dolly")
    float DollySpeed = 100.0f;

    /** 当前推拉方向：-1 后退, 0 停止, 1 前进 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dolly")
    float DollyDirection = 0.0f;

    /** 最小焦距限制 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dolly")
    float MinFocalLength = 20.0f;

    /** 最大焦距限制 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dolly")
    float MaxFocalLength = 200.0f;
};
```

```cpp
// SimpleDollyModifier.cpp
#include "SimpleDollyModifier.h"
#include "CineCameraComponent.h"

USimpleDollyModifier::USimpleDollyModifier()
{
    // 定义连接点，供 UI 控件绑定
    ConnectionPoints.Add(TEXT("DollyDirection"), FVCamModifierConnectionPoint{});
    ConnectionPoints.Add(TEXT("DollySpeed"), FVCamModifierConnectionPoint{});
}

void USimpleDollyModifier::Initialize(UVCamModifierContext* Context, UInputComponent* InputComponent)
{
    Super::Initialize(Context, InputComponent);
}

void USimpleDollyModifier::Apply(UVCamModifierContext* Context, UCineCameraComponent* CameraComponent, const float DeltaTime)
{
    if (!CameraComponent || FMath::IsNearlyZero(DollyDirection))
    {
        return;
    }

    // 通过修改焦距模拟推拉效果
    float NewFocalLength = CameraComponent->CurrentFocalLength + (DollyDirection * DollySpeed * DeltaTime * 0.1f);
    CameraComponent->CurrentFocalLength = FMath::Clamp(NewFocalLength, MinFocalLength, MaxFocalLength);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 协议支持，用于接收外部设备的摄像机数据 |
| `MediaUtils` | 媒体捕获和输出工具 |
| `RemoteSession` | Unreal Remote Session 协议，用于与移动设备通信 |
| `PixelStreaming` | Pixel Streaming 集成，用于浏览器端虚拟摄像机 |
| `EnhancedInput` | 增强输入系统，处理虚拟摄像机设备的输入 |
| `Concert` / `ConcertSyncCore` | 多用户编辑支持，同步虚拟摄像机状态 |
| `LevelEditor` | 编辑器视口操作（PixelStreamingVCam 模块） |
| `UnrealEd` | 编辑器功能（PixelStreamingVCam 模块） |

## 维护状态

### 近期更新

```
- f6a25eeed3e Virtual Camera: After deactivating VCam, the viewport FOV is now restored to what it was before.
- 28bb0966d63 [SubsystemCollection] removed deprecated methods
- 551d3a5b58d Address bug hawk and CIS deprecation warnings.
```

### 维护评价

- **创建时间**：2023 年 2 月，约 2 年历史
- **实验性状态**：`IsBetaVersion = true`，`EnabledByDefault = false`，需要手动启用
- **活跃度**：近期有功能性更新（视口 FOV 恢复修复）和维护性更新（废弃方法清理、编译警告修复），表明仍在积极维护
- **代码规模**：368 个源文件，属于大型插件，架构成熟
- **已知限制**：
  - Beta 状态，API 可能在未来版本发生变化
  - `UVCamOutputComposure` 已在 5.7 标记为废弃
  - 部分 API（如 `InputKey(FInputKeyParams)`）在 5.6 标记为废弃
- **推荐程度**：✅ 推荐用于虚拟制片项目。作为 Epic 官方维护的虚拟摄像机框架，它是 VirtualCamera 内容插件的运行时基础，架构设计合理且持续更新。注意 Beta 状态意味着升级时需关注 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- [VirtualCamera 内容插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCamera)（配套内容资产）