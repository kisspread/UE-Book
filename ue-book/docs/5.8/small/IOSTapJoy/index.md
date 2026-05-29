# IOS TapJoy Advertising Provider

> IOS TapJoy Provider

| 属性 | 值 |
|---|---|
| 中文名 | iOS TapJoy 广告 |
| 分类 | Advertising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IOSTapJoy` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-05-07 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Advertising/IOSTapJoy) | |

## 用途

为 UE5 的广告系统提供 iOS 平台上的 TapJoy SDK 集成。TapJoy 是一个移动应用变现平台，提供奖励视频广告、应用内广告墙等变现方式。该插件实现了 UE5 广告提供者接口（`IAdvertisingProvider`），使项目能够通过 TapJoy 在 iOS 设备上展示广告并获取收益。

**注意**：该插件仅限 iOS 平台使用（`PlatformAllowList: ["IOS"]`），且默认未启用。

## 使用场景

- 你在开发 iOS 移动游戏，需要集成 TapJoy 广告变现 → 启用此插件
- 你需要通过 TapJoy 的奖励视频广告为玩家提供游戏内货币/道具 → 使用此插件对接 UE5 广告系统

## 蓝图用法

该插件作为广告提供者（Provider）集成到 UE5 的广告子系统中，不直接暴露蓝图节点。广告展示通过引擎内置的广告接口调用。

### 使用方式

1. 在项目设置或 `DefaultEngine.ini` 中启用插件
2. 配置 TapJoy App ID 和相关密钥
3. 通过引擎广告子系统发起广告请求

## C++ 用法

### 头文件引入

```cpp
#include "IOSTapJoy.h"
```

### 基本用法

该插件作为 Runtime 广告提供者模块自动注册。启动应用后，引擎的 `UAdvertisingSubsystem` 会发现并加载此 Provider，无需手动实例化。

**典型集成流程**：

```cpp
// 广告通常通过引擎子系统调用，而非直接调用此插件
// 示例：通过广告子系统请求广告展示
if (UAdvertisingSubsystem* AdSubsystem = UAdvertisingSubsystem::Get())
{
    // 引擎会自动选择已注册的广告提供者（包括 TapJoy）
}
```

**注意**：由于该插件仅有一个源文件且为 stub 级实现，可公开调用的 API 极为有限。

## Demo 示例

该插件为引擎内置广告提供者，本身不提供独立示例。集成方式取决于引擎广告子系统的配置。

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。该插件结构极简，仅包含一个 Runtime 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-27 | `e0e44021` | [TapJoy] | TapJoy 相关更新 |
| 2026-01-14 | `1a097717` | Fix IOS CIS Issues. | 修复 iOS 持续集成问题 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将供应商链接更新为安全协议 |
| 2022-09-10 | `0eeac455` | Pass 3 on cleaning up build.cs files. | 第三轮清理 Build.cs 文件 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 引擎版本合并 |

### 维护评价

- **插件年龄**：超过 11 年，属于早期实现
- **源码规模**：仅 1 个源文件，初始提交即为 "stub"，功能实现极为精简
- **近期活动**：2026 年初有 iOS CI 修复和 TapJoy 相关更新，表明仍在维护
- **限制**：
  - 仅支持 iOS 平台
  - 默认未启用（`EnabledByDefault: false`）
  - 无公开头文件，API 极为有限
  - 需要额外配置 TapJoy SDK 凭据

该插件作为 Epic 官方维护的内置广告提供者仍在跟随引擎更新，但功能较为基础。如果你的项目确实需要在 iOS 上使用 TapJoy 广告服务，可以启用此插件；但建议确认 TapJoy SDK 版本兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Advertising/IOSTapJoy)
- [TapJoy 官方文档](https://dev.tapjoy.com/)（第三方 SDK 文档）