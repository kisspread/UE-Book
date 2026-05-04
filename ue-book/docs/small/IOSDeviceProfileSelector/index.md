# IOS Device Profile Selector

> IOS Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ true |
| 包含内容 | false |
| 模块 | IOSDeviceProfileSelector (RuntimeNoCommandlet) |
| 加载阶段 | PostConfigInit |
| 支持平台 | IOS, TVOS, VisionOS |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（>10年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/IOSDeviceProfileSelector) | |

## 用途

这是一个极小的系统级 plugin，为 iOS/tvOS/visionOS 平台提供 **设备配置文件选择器**。

UE5 的 Device Profile 系统允许根据硬件型号自动切换渲染、画质等设置。每个平台需要一个 Selector Module 来告诉引擎"当前运行在什么设备上，应该使用哪个 Profile"。本 plugin 就是 iOS 系列平台的这个角色——它在应用启动时查询设备硬件信息，返回对应的 Device Profile 名称（如 `iPhone15,2` → `iPhone14Pro` Profile）。

**它不暴露任何蓝图节点或 API 给游戏逻辑**，完全在引擎内部自动运行。

## 使用场景

- 你的项目需要部署到 iOS/tvOS/visionOS → 此 plugin 默认启用，无需额外操作
- 你需要为不同 iOS 设备配置不同的画质/渲染设置 → 在 Device Profiles 中为每种设备型号创建 Profile，本 plugin 负责在运行时自动选择
- 你在使用 Vision Pro → 本 plugin 已支持 VisionOS 平台

## 工作原理

整个 plugin 只有一个核心函数 `GetRuntimeDeviceProfileName()`：

```cpp
FString const FIOSDeviceProfileSelectorModule::GetRuntimeDeviceProfileName()
{
    FString ProfileName = FPlatformMisc::GetDefaultDeviceProfileName();
    if (ProfileName.IsEmpty())
    {
        ProfileName = FPlatformProperties::PlatformName();
    }
    UE_LOG(LogIOS, Log, TEXT("Selected Device Profile: [%s]"), *ProfileName);
    return ProfileName;
}
```

逻辑非常简单：
1. 调用 `FPlatformMisc::GetDefaultDeviceProfileName()` 获取设备标识（如 `iPhone15,2`）
2. 如果为空，回退到平台名称（`IOS` / `TVOS` / `VisionOS`）
3. 通过 `LogIOS` 日志输出选中的 Profile 名称，便于调试

引擎在启动时会调用此接口，根据返回值加载对应的 Device Profile 配置。

## 蓝图用法

本 plugin 无蓝图接口。它不包含任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`，所有逻辑在引擎内部透明执行。

## C++ 用法

### 头文件引入

```cpp
#include "IDeviceProfileSelectorModule.h"
```

### 基本用法

本 plugin 不设计为被游戏代码直接调用。它通过 `IDeviceProfileSelectorModule` 接口注册到引擎的 Device Profile 系统中，由引擎自动使用。

如果你需要在代码中获取当前生效的 Device Profile 名称，可以通过引擎的全局接口：

```cpp
// 获取当前运行时 Device Profile 名称
IDeviceProfileSelectorModule* SelectorModule = 
    FModuleManager::GetModulePtr<IDeviceProfileSelectorModule>(TEXT("IOSDeviceProfileSelector"));
if (SelectorModule)
{
    FString ProfileName = SelectorModule->GetRuntimeDeviceProfileName();
    UE_LOG(LogTemp, Log, TEXT("Current Device Profile: %s"), *ProfileName);
}
```

> ⚠️ 此接口仅在 IOS/TVOS/VisionOS 平台可用，在其他平台此模块不会加载。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎模块，提供 `FPlatformMisc` 等平台抽象 |
| `CoreUObject` | 对象系统（私有依赖） |
| `Engine` | 引擎核心，提供 `IDeviceProfileSelectorModule` 接口（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-06-30 | `8d6eb87c` | Hooked up the VisionPro simulator deviceprofile to disable virtual streaming; Made Simulator device strings for IOS platforms | 新增 VisionOS 支持，适配 Apple Vision Pro 模拟器 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol | URL 协议升级（http→https），无功能变更 |
| 2022-09-10 | `0eeac455` | Pass 3 on cleaning up build.cs files | 构建文件清理，无功能变更 |

### 维护评价

- **创建时间**: 2014年3月，距今约12年，属于最早的 UE4 时代 plugin
- **代码规模**: 极小，仅 2 个源文件，总共约 60 行有效代码
- **最近功能性更新**: 2023年6月（VisionOS 支持），约3年前
- **维护状态**: **维护中但极低频**。代码极其简单稳定，几乎不需要修改。2022-2023 年的更新都是构建系统清理和平台适配，非功能变更
- **风险**: 无。代码逻辑简单且依赖稳定的平台 API，不存在已知问题
- **推荐**: 默认启用即可，无需额外关注。如果你只针对 iOS 设备做性能适配，此 plugin 是整个 Device Profile 链条的起点

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/IOSDeviceProfileSelector)
- [IDeviceProfileSelectorModule 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Public/IDeviceProfileSelectorModule.h)
