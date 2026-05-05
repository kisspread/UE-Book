# HP Motion Controller

> Controller mappings for the HP Reverb G2 motion controller in OpenXR and SteamVR

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | HPMotionController (Runtime) |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HPMotionController) | |

## 用途

为 HP Reverb G2 VR 头显的运动控制器提供 OpenXR 输入映射。该 plugin 注册了 `XR_EXT_HP_MIXED_REALITY_CONTROLLER` OpenXR 扩展，将 HP Reverb G2 控制器的按钮、摇杆和扳机映射为 UE 的 FKey 输入键，使项目可以通过标准输入系统读取 HP 控制器的状态。

它并不提供任何蓝图节点或 C++ API —— 全部功能是通过 OpenXR 扩展插件机制（`IOpenXRExtensionPlugin`）在模块启动时自动注册输入键和控制器模型。

## 使用场景

- 你正在开发支持 HP Reverb G2 头显的 VR 应用 → 启用此 plugin，即可在 Enhanced Input 或传统输入映射中使用 HP 控制器专属按键
- 你需要同时支持多种 VR 控制器（Quest、Vive、Index、HP Reverb G2）→ 启用此 plugin 作为 OpenXR 扩展，运行时自动识别 HP 控制器
- 你只需要支持 Quest 或 Vive 控制器 → 不需要此 plugin

## 蓝图用法

此 plugin 不暴露任何 BlueprintCallable 函数。它的作用是向引擎注册一组 FKey 输入键，你可以在 **项目设置 → Input** 或 **Enhanced Input** 中看到这些键。

### 注册的输入键

所有按键均在 `HPMixedRealityController` 分类下。

**左手 (Left)**

| 键名 | 类型 | 说明 |
|---|---|---|
| `HPMixedRealityController_Left_X_Click` | Digital | X 按钮按下 |
| `HPMixedRealityController_Left_Y_Click` | Digital | Y 按钮按下 |
| `HPMixedRealityController_Left_Menu_Click` | Digital | Menu 按钮 |
| `HPMixedRealityController_Left_Grip_Click` | Digital | Grip 按下 |
| `HPMixedRealityController_Left_Grip_Axis` | Axis (0-1) | Grip 握力轴 |
| `HPMixedRealityController_Left_Trigger_Click` | Digital | Trigger 按下 |
| `HPMixedRealityController_Left_Trigger_Axis` | Axis (0-1) | Trigger 扳机轴 |
| `HPMixedRealityController_Left_Thumbstick_Click` | Digital | 摇杆按下 |
| `HPMixedRealityController_Left_Thumbstick_X` | Axis (-1~1) | 摇杆 X 轴 |
| `HPMixedRealityController_Left_Thumbstick_Y` | Axis (-1~1) | 摇杆 Y 轴 |

**右手 (Right)**

| 键名 | 类型 | 说明 |
|---|---|---|
| `HPMixedRealityController_Right_A_Click` | Digital | A 按钮按下 |
| `HPMixedRealityController_Right_B_Click` | Digital | B 按钮按下 |
| `HPMixedRealityController_Right_Menu_Click` | Digital | Menu 按钮 |
| `HPMixedRealityController_Right_Grip_Click` | Digital | Grip 按下 |
| `HPMixedRealityController_Right_Grip_Axis` | Axis (0-1) | Grip 握力轴 |
| `HPMixedRealityController_Right_Trigger_Click` | Digital | Trigger 按下 |
| `HPMixedRealityController_Right_Trigger_Axis` | Axis (0-1) | Trigger 扳机轴 |
| `HPMixedRealityController_Right_Thumbstick_Click` | Digital | 摇杆按下 |
| `HPMixedRealityController_Right_Thumbstick_X` | Axis (-1~1) | 摇杆 X 轴 |
| `HPMixedRealityController_Right_Thumbstick_Y` | Axis (-1~1) | 摇杆 Y 轴 |

### 使用示例（蓝图描述）

1. 在 **Edit → Project Settings → Input → Action Mappings** 中添加新 Action
2. 在下拉键列表中搜索 `HP Mixed Reality`，选择对应按键（如 `HP Mixed Reality (L) Trigger`）
3. 在蓝图中使用 `EnhancedActionMapping` 或 `Input Action` 节点读取该输入

或者使用 Enhanced Input：
1. 创建 `Input Action` 资产，在 `Keys` 中添加 `HPMixedRealityController_*` 键
2. 创建 `Input Mapping Context`，绑定该 Input Action

## C++ 用法

此 plugin 没有公共 C++ API。所有功能通过 OpenXR 扩展机制自动生效。

### 模块加载

模块在 `PostConfigInit` 阶段加载（非常早），通过 `IOpenXRExtensionPlugin` 的 modular feature 注册到 OpenXR 子系统。启用 plugin 后无需任何额外代码。

### 关键实现细节

`FHPMotionControllerModule` 实现了 `IOpenXRExtensionPlugin` 接口，主要回调：

- `GetRequiredExtensions()` — 请求 `XR_EXT_HP_MIXED_REALITY_CONTROLLER` 扩展
- `PostCreateInstance()` — 解析 interaction profile 路径 `/interaction_profiles/hp/mixed_reality_controller`，关联左右手控制器的 3D 模型
- `GetInteractionProfiles()` — 注册 `HPMixedRealityController` 前缀的交互配置
- `GetControllerModel()` — 返回左右手控制器的 Mesh 资产路径

## Demo 示例

由于此 plugin 是纯注册型扩展，没有可独立演示的代码。启用后的完整工作流程：

```cpp
// Build.cs — 如果你需要在自定义模块中引用 HP 控制器键
PublicDependencyModuleNames.Add("InputCore");  // FKey 定义在此模块

// 在你的 Actor/Component 中绑定 HP 控制器输入
// 通过 Enhanced Input 或传统 InputComponent 均可
```

## 模块依赖

此 plugin 的 Build.cs 声明的依赖均为 **Private**（不传递给使用者）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | FKey / EKeys 输入键系统 |
| `OpenXRHMD` | OpenXR HMD 运行时模块 |
| `OpenXR` | OpenXR 第三方库（静态链接） |

**插件依赖**：`OpenXR` plugin 必须启用（已在 .uplugin 中声明）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-21 | `82674f19` | OpenXR 扩展名改用 openxr.h 宏定义 | 代码质量改进，消除硬编码字符串，降低维护成本 |
| 2024-08-01 | `0ba65eae` | 支持一个扩展插件注册多个 interaction profile | 基础架构更新，适配 OpenXR 框架重构 |
| 2023-02-16 | `75ceaf89` | 清理冗余的 OpenXR include 路径 | 代码清理 |

### 维护评价

- **创建时间**：2020-10-22，约 5.5 年历史
- **活跃度**：最近更新在 2025-07，属于**活跃维护**
- **更新模式**：随引擎基础设施升级被动更新，plugin 本身功能稳定
- **代码规模**：仅 2 个源文件（.h + .cpp），~200 行代码，极其简洁
- **注意事项**：
  - `EnabledByDefault: false` — 需手动在 Plugins 面板中启用
  - 仅支持 Win64 平台
  - 依赖 `XR_EXT_HP_MIXED_REALITY_CONTROLLER` OpenXR 扩展，需要 OpenXR 运行时支持
  - HP Reverb G2 已停产，该 plugin 的长期前景取决于 HP VR 产品的后续发展
- **推荐**：如果你的用户群体使用 HP Reverb G2，此 plugin 是必需的。否则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HPMotionController)
- [OpenXR EXT_HP_mixed_reality_controller 规范](https://www.khronos.org/registry/OpenXR/specs/1.0/html/xrspec.html#XR_EXT_hp_mixed_reality_controller)
- [OpenXR plugin（前置依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXR)
