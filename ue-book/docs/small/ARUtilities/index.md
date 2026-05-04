# AR Utilities

> Utility code and content for AR systems

| 属性 | 值 |
|---|---|
| 分类 | Augmented Reality |
| 默认启用 | 是（但仅限 LiveLinkHub 程序） |
| 包含内容 | 是（含 7 个材质资产） |
| 模块 | ARUtilities (Runtime) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5.6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/ARUtilities) | |

> **重要限制**：此 plugin 的 `SupportedPrograms` 限定为 `LiveLinkHub`，模块加载阶段也设置了 `ProgramAllowList: ["LiveLinkHub"]`。这意味着该 plugin **仅在 LiveLinkHub 程序中可用**，在标准 Unreal Editor 或游戏打包中不会加载。

## 用途

ARUtilities 是 Epic 为 AR（增强现实）场景提供的一组工具类 plugin，主要解决两个问题：

1. **AR 相机透视渲染（Passthrough）**：将 AR 设备的摄像头画面作为材质贴图应用到场景中的 Mesh 上，实现"透视"效果——让虚拟物体叠加在真实世界画面上。
2. **AR 动作捕捉数据重定向（LiveLink Retargeting）**：将 AR 平台（如 ARKit）的全身/手部骨骼追踪数据通过 LiveLink 管线重定向到 UE 的角色骨骼上。

该 plugin 依赖 LiveLink plugin，并包含一套预置材质资产（屏幕空间透视材质、深度着色材质等），开发者可以直接使用或作为自定义 AR 材质的起点。

## 使用场景

- 你在做 **AR/MR 应用**，需要把设备摄像头画面渲染到 MR Mesh 上 → 使用 `AARPassthroughManager` + `UPassthroughMaterialUpdateComponent`
- 你需要将 **ARKit 全身动捕数据**通过 LiveLink 驱动 UE 角色动画 → 创建 `UARLiveLinkRetargetAsset` 子类并配置骨骼映射
- 你需要在材质中**手动更新 AR 摄像头纹理或深度数据** → 使用 `UARUtilitiesFunctionLibrary` 的蓝图节点

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateCameraTextureParam` | 更新材质的摄像头纹理参数（自动区分普通纹理和 External Texture） | `UARUtilitiesFunctionLibrary` |
| `UpdateSceneDepthTexture` | 更新材质的场景深度纹理参数 | `UARUtilitiesFunctionLibrary` |
| `UpdateWorldToMeterScale` | 更新材质的世界到米缩放参数 | `UARUtilitiesFunctionLibrary` |
| `AddAffectedComponent` | 将一个 PrimitiveComponent 加入透视渲染列表 | `UPassthroughMaterialUpdateComponent` |
| `RemoveAffectedComponent` | 从透视渲染列表移除组件 | `UPassthroughMaterialUpdateComponent` |
| `SetPassthroughDebugColor` | 设置透视调试颜色（用于可视化受影响的 Mesh） | `UPassthroughMaterialUpdateComponent` |
| `GetPassthroughMaterialUpdateComponent` | 获取管理器内置的材质更新组件 | `AARPassthroughManager` |

### 可编辑属性（Details 面板）

**AARPassthroughManager：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `ARComponentClasses` | `TArray<TSubclassOf<UARComponent>>` | 要收集的 AR 组件类型，默认为 `UARMeshComponent` |

**UPassthroughMaterialUpdateComponent：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `TextureType` | `EARTextureType` | 使用哪种 AR 纹理，默认 `CameraImage` |
| `PassthroughMaterial` | `UMaterialInterface*` | 普通摄像头纹理的材质 |
| `PassthroughMaterialExternalTexture` | `UMaterialInterface*` | External Texture 类型的材质 |
| `PassthroughDebugColor` | `FLinearColor` | 调试颜色，默认白色 |

### 使用示例（蓝图描述）

**自动透视渲染（最简用法）：**

1. 在场景中放置一个 `AARPassthroughManager` Actor
2. 在 Details 面板中配置 `ARComponentClasses`（默认已包含 `ARMeshComponent`）
3. 运行时，Manager 会自动监听 AR Actor 的生成，将 MR Mesh 加入透视渲染
4. 无需额外蓝图连线，一切在 `BeginPlay` 中自动注册

**手动控制透视渲染：**

1. 获取场景中的 `AARPassthroughManager` → 调用 `GetPassthroughMaterialUpdateComponent`
2. 调用 `AddAffectedComponent`，传入你的 `UPrimitiveComponent` 引用
3. 每帧 `TickComponent` 会自动更新摄像头纹理到材质上
4. 可随时调用 `RemoveAffectedComponent` 移除

## C++ 用法

### 头文件引入

```cpp
#include "ARUtilitiesFunctionLibrary.h"
#include "ARPassthroughManager.h"
#include "PassthroughMaterialUpdateComponent.h"
#include "ARLiveLinkRetargetAsset.h"
```

### 基本用法 — 更新材质中的 AR 纹理

```cpp
// 获取 AR 摄像头纹理
UTexture* CameraTexture = UARBlueprintLibrary::GetARTexture(EARTextureType::CameraImage);

// 创建动态材质实例
UMaterialInstanceDynamic* DynMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, this);

// 更新摄像头纹理（自动处理普通/External Texture 差异）
UARUtilitiesFunctionLibrary::UpdateCameraTextureParam(DynMaterial, CameraTexture, 1.0f);

// 更新深度纹理（如果需要）
UTexture* DepthTexture = UARBlueprintLibrary::GetARTexture(EARTextureType::SceneDepthMap);
UARUtilitiesFunctionLibrary::UpdateSceneDepthTexture(DynMaterial, DepthTexture, 1.0f);

// 更新世界缩放
UARUtilitiesFunctionLibrary::UpdateWorldToMeterScale(DynMaterial, 100.0f);
```

来源：`ARUtilitiesFunctionLibrary.cpp`

### 进阶用法 — 自定义 LiveLink 重定向

要使用 AR LiveLink 重定向功能，需要创建 `UARLiveLinkRetargetAsset` 的子类：

```cpp
// ARLiveLinkRetargetAsset 是 Abstract 类，不能直接实例化
// 需要创建 Blueprint 子类或 C++ 子类，并在编辑器中设置 SourceType 和 BoneMap

// 如需实现平台特定的重定向逻辑，注册 Modular Feature：
// IModularFeatures::Get().RegisterModularFeature(
//     IARLiveLinkRetargetingLogic::GetModularFeatureName(),
//     &YourRetargetLogicInstance
// );
```

`UARLiveLinkRetargetAsset` 内置了 ARKit → Mannequin 骨骼的默认映射表（52 根骨骼），在编辑器中将 `SourceType` 设为 `ARKitPoseTracking` 时自动生成。

## 预置材质资产

Plugin 内置了以下材质，路径前缀为 `/ARUtilities/Materials/`：

| 资产 | 说明 |
|---|---|
| `M_ScreenSpacePassthroughCamera` | 屏幕空间透视摄像头材质（默认） |
| `M_PassthroughCamera` | 标准透视摄像头材质 |
| `M_DepthColoration` | 深度着色材质 |
| `MI_ScreenSpacePassthroughCameraExternalTexture` | External Texture 版屏幕空间材质（默认） |
| `MI_PassthroughCameraExternalTexture` | External Texture 版标准材质 |
| `MF_DistanceColorLerp` | 距离颜色插值材质函数 |
| `DummyExternalTexture` | 占位 External Texture |

### 材质参数名称约定

这些预置材质使用统一的参数命名，`UARUtilitiesFunctionLibrary` 会自动设置：

| 参数名 | 类型 | 来源函数 |
|---|---|---|
| `CameraTexture` | Texture | `UpdateCameraTextureParam`（普通纹理） |
| `ExternalCameraTexture` | TextureExternal | `UpdateCameraTextureParam`（External 纹理） |
| `ColorScale` | Scalar | `UpdateCameraTextureParam` |
| `SceneDepthTexture` | Texture | `UpdateSceneDepthTexture` |
| `DepthToMeterScale` | Scalar | `UpdateSceneDepthTexture` |
| `WorldToMeterScale` | Scalar | `UpdateWorldToMeterScale` |
| `DebugColor` | Vector | `SetPassthroughDebugColor`（由组件自动设置） |

## 模块依赖

从 `ARUtilities.Build.cs` 提取：

### Public 依赖（你的模块也需要依赖）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `LiveLinkAnimationCore` | LiveLink 动画核心，用于骨骼重定向 |

### Private 依赖（plugin 内部使用）

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `AugmentedReality` | AR 核心模块（ARBlueprintLibrary 等） |
| `MRMesh` | Mixed Reality Mesh 组件 |

### Plugin 依赖

| Plugin | 说明 |
|---|---|
| `LiveLink` | LiveLink 框架，必需 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-11-16 | `65c4f129` | Add livelinkhub to program allowlists; Add optional plugin dependencies to LiveLinkHub | 将此 plugin 的 SupportedPrograms 和模块 ProgramAllowList 限定到 LiveLinkHub，表明 Epic 将其定位为 LiveLinkHub 专用工具 |
| 2023-01-16 | `bbc37aa2` | Another batch IWYU updates to reduce number of includes used in files | 编译优化，IWYU 合规性修复，非功能性改动 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol | .uplugin 元数据更新（HTTPS 链接），非功能性改动 |

### 维护评价

- **创建时间**：2020 年 9 月，约 5.6 年历史
- **最近实质性更新**：2023 年 11 月（限定到 LiveLinkHub），距今约 2.5 年
- **维护状态**：**维护不活跃** — 最近 3 次提交均为非功能性改动（IWYU、链接更新、程序限制调整），最后一次实质性功能更新可能在 2020-2021 年间
- **注意**：该 plugin 已被限定为仅在 LiveLinkHub 中可用，标准 UE 编辑器和游戏中无法直接使用
- **推荐**：如果你在开发 LiveLinkHub 相关的 AR 工作流，此 plugin 提供了现成的透视渲染和骨骼重定向基础设施；否则其功能对你不可见。对于标准 UE 项目中的 AR 开发，应直接使用 `AugmentedReality` 模块和 `ARBlueprintLibrary`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/ARUtilities)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：未找到（Engine 目录下未发现 ARUtilities 相关测试文件）
