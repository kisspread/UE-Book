# Android Device Profile Selector

> Android Device Profile Selector used show selection of device profiles on hardware

| 属性 | 值 |
|---|---|
| 分类 | Device Profile Selectors |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 否 |
| 模块 | AndroidDeviceProfileSelector (Editor), AndroidDeviceProfileCommandlets (Editor), AndroidDeviceProfileSelectorRuntime (RuntimeNoCommandlet) |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidDeviceProfileSelector) | |

## 用途

这是一个**自动设备检测与配置匹配系统**。当你的 UE5 游戏运行在 Android 设备上时，引擎需要知道"这是什么级别的硬件"，然后自动应用对应的画质配置（Device Profile）。这个 plugin 就是做这件事的——它收集当前设备的硬件信息（GPU 型号、Android 版本、内存大小、Vulkan 支持情况等），然后用一套可配置的匹配规则来确定应该使用哪个 Device Profile。

**解决的核心问题**：Android 生态碎片化严重，不同设备的 GPU、内存、驱动版本差异巨大。手动为每种设备配置画质参数不现实，因此需要一个基于规则的自动匹配系统。

**工作原理**：
1. **Runtime 模块**（`AndroidDeviceProfileSelectorRuntime`）在 Android 设备启动时收集 15+ 项硬件参数
2. **匹配引擎**（`FAndroidDeviceProfileSelector`）读取 `DeviceProfiles.ini` 中的匹配规则
3. 规则按顺序检查，**第一个完全匹配的规则胜出**，返回对应的 Profile 名称
4. 引擎加载该 Profile 对应的画质配置（纹理质量、分辨率缩放、Vulkan/GL 切换等）

## 使用场景

- 你做了一个需要在各种 Android 手机上运行的游戏 → **默认已启用**，不需要额外操作
- 你需要为特定型号手机定制画质 → 在 `DeviceProfiles.ini` 中添加匹配规则
- 你需要为某款新 GPU（如 Adreno 8xx）启用 Vulkan → 添加基于 `SRC_GpuFamily` 的正则匹配规则
- 你需要在编辑器中预览特定 Android 设备的效果 → 使用 ADB Commandlet 导出设备参数 JSON
- 你做的是 VR 应用（Meta Quest 等）→ 系统会根据 `SRC_HMDSystemName` 自动匹配 Quest 设备 Profile
- 你需要为 Houdini 模拟器（Intel 芯片跑 ARM 应用）做特殊处理 → 系统通过 `SRC_UsingHoudini` 自动检测

## 蓝图用法

此 plugin **不暴露任何蓝图节点**。它是一个纯 C++ 的底层系统，在引擎启动时自动执行设备检测和 Profile 选择。所有配置通过 `.ini` 文件完成，不涉及蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "AndroidDeviceProfileSelector.h"
```

### 核心类：FAndroidDeviceProfileSelector

这是匹配引擎的核心类，所有方法都是 static。

```cpp
// 获取当前设备的匹配 Profile 名称
// FallbackProfileName: 如果没有任何规则匹配，返回此默认值
FString ProfileName = FAndroidDeviceProfileSelector::FindMatchingProfile(TEXT("Android"));

// 获取当前加载的匹配规则总数
int32 NumRules = FAndroidDeviceProfileSelector::GetNumProfiles();

// 获取当前设备的所有选择器参数
const TMap<FName, FString>& Props = FAndroidDeviceProfileSelector::GetSelectorProperties();
```

### 设备参数源（Source Properties）

匹配规则中可用的设备参数定义在 `FAndroidProfileSelectorSourceProperties` 命名空间中：

| 参数名 | 说明 | 示例值 |
|---|---|---|
| `SRC_GPUFamily` | GPU 系列名称 | `Adreno (TM) 740` |
| `SRC_GLVersion` | OpenGL/Vulkan 驱动版本 | `V@512.0` |
| `SRC_VulkanAvailable` | 是否支持 Vulkan | `true` / `false` |
| `SRC_VulkanVersion` | Vulkan 版本 | `1.1.128` |
| `SRC_AndroidVersion` | Android 系统版本 | `13` |
| `SRC_DeviceMake` | 设备制造商 | `samsung` |
| `SRC_DeviceModel` | 设备型号 | `SM-S918B` |
| `SRC_DeviceBuildNumber` | 系统构建号 | `TP1A.220624.014` |
| `SRC_UsingHoudini` | 是否使用 Houdini ARM 模拟 | `true` / `false` |
| `SRC_Hardware` | 硬件标识 | `qcom` |
| `SRC_Chipset` | 芯片组 | `exynos2400` |
| `SRC_HMDSystemName` | VR 头显名称 | `Meta Quest 3` |
| `SRC_TotalPhysicalGB` | 总物理内存（GB，含舍入） | `8` |
| `SRC_SM5Available` | 是否支持 SM5（Desktop Vulkan） | `true` / `false` |
| `SRC_VKQuality` | Vulkan 质量推荐等级 | （由 `GetVKQualityRecommendation()` 返回） |
| `SRC_ResolutionX/Y` | 屏幕分辨率 | `2340` / `1080` |
| `SRC_Insets*` | 安全区域 insets | `0.0` |

### 匹配规则配置（INI）

匹配规则定义在 `DeviceProfiles.ini` 中，section 为 `[/Script/AndroidDeviceProfileSelector.AndroidDeviceProfileMatchingRules]`。

每条规则的结构：
```ini
+MatchProfile=(Profile="ProfileName",Match=((SourceType=SRC_XXX,CompareType=CMP_XXX,MatchString="value"), ...))
```

**SourceType** 枚举（匹配数据源）：

| 枚举值 | 说明 |
|---|---|
| `SRC_GpuFamily` | GPU 系列 |
| `SRC_GlVersion` | GL/Vulkan 驱动版本 |
| `SRC_AndroidVersion` | Android 版本 |
| `SRC_DeviceMake` | 制造商 |
| `SRC_DeviceModel` | 型号 |
| `SRC_DeviceBuildNumber` | 构建号 |
| `SRC_VulkanVersion` | Vulkan 版本 |
| `SRC_UsingHoudini` | Houdini 模拟 |
| `SRC_VulkanAvailable` | Vulkan 可用性 |
| `SRC_CommandLine` | 命令行参数 |
| `SRC_Hardware` | 硬件标识 |
| `SRC_Chipset` | 芯片组 |
| `SRC_ConfigRuleVar` | ConfigRules 变量 |
| `SRC_HMDSystemName` | VR 头显名称 |
| `SRC_SM5Available` | SM5 可用性 |
| `SRC_VKQuality` | VK 质量推荐 |
| `SRC_PreviousRegexMatch` | 上一次正则匹配的捕获组 |

**CompareType** 枚举（比较方式）：

| 枚举值 | 说明 |
|---|---|
| `CMP_Equal` | 精确匹配 |
| `CMP_NotEqual` | 不等于 |
| `CMP_Less` / `CMP_LessEqual` | 小于 / 小于等于 |
| `CMP_Greater` / `CMP_GreaterEqual` | 大于 / 大于等于 |
| `CMP_EqualIgnore` ~ `CMP_NotEqualIgnore` | 忽略大小写版本 |
| `CMP_Regex` | 正则表达式匹配（捕获组1存入 `SRC_PreviousRegexMatch`） |
| `CMP_Hash` | SHA1 哈希匹配（格式：`Salt|Hash` 或纯 Hash） |

### 使用示例：添加自定义匹配规则

在你的项目 `DeviceProfiles.ini` 中：

```ini
; 为三星旗舰机型启用高画质 Vulkan Profile
[/Script/AndroidDeviceProfileSelector.AndroidDeviceProfileMatchingRules]
+MatchProfile=(Profile="Samsung_S24_Ultra",Match=((SourceType=SRC_DeviceMake,CompareType=CMP_EqualIgnore,MatchString="samsung"),(SourceType=SRC_DeviceModel,CompareType=CMP_Equal,MatchString="SM-S928B"),(SourceType=SRC_VulkanAvailable,CompareType=CMP_Equal,MatchString="true")))

; 基于 GPU 正则 + Android 版本级联匹配
; 先用正则提取 Android 版本号，再用 SRC_PreviousRegexMatch 做数值比较
+MatchProfile=(Profile="Adreno7xx_Android13Plus_Vulkan",Match=((SourceType=SRC_GpuFamily,CompareType=CMP_Regex,MatchString="Adreno \\\\(TM\\\\) 7[0-9][0-9]"),(SourceType=SRC_AndroidVersion,CompareType=CMP_Regex,MatchString="([0-9]+).*"),(SourceType=SRC_PreviousRegexMatch,CompareType=CMP_GreaterEqual,MatchString="13"),(SourceType=SRC_VulkanAvailable,CompareType=CMP_Equal,MatchString="true")))

; 基于内存大小的匹配
+MatchProfile=(Profile="Android_LowMemory",Match=((SourceType=SRC_TotalPhysicalGB,CompareType=CMP_LessEqual,MatchString="3")))

; 基于 ConfigRules 变量的匹配
+MatchProfile=(Profile="Custom_Device",Match=((SourceType=SRC_ConfigRuleVar,CompareType=CMP_Equal,MatchString="custom_gpu|Qualcomm Adreno")))
```

> **重要**：规则按顺序检查，**第一个所有条件都满足的规则胜出**。因此应将更具体的规则放在前面，通用的 fallback 规则放在后面。

### Hash 比较模式

`CMP_Hash` 用于在不暴露设备标识的情况下做匹配。格式：

```ini
; MatchString = "Salt|SHA1(SRC_DeviceModel + Salt + Pepper)"
; Pepper 通过 Build.cs 中的 HASH_PEPPER_SECRET_GUID 宏注入
+MatchProfile=(Profile="SpecificDevice",Match=((SourceType=SRC_DeviceModel,CompareType=CMP_Hash,MatchString="MySalt|d9e5cbd6b0e4dba00edd9de92cf64ee4c3f3a2db")))
```

生成方式：
```bash
printf "PhoneModelMySalt" | openssl dgst -sha1 -hex
```

要启用 Pepper，需在 `Engine/Config/BaseEngine.ini` 中配置：
```ini
[AndroidDPSBuildSettings]
SecretGuid=你的GUID
```

### 运行时模块接口

`FAndroidDeviceProfileSelectorRuntimeModule` 实现了 `IDeviceProfileSelectorModule` 接口，引擎在 Android 平台启动时自动调用：

```cpp
// 引擎内部调用流程（无需手动调用）：
// 1. GetDeviceSelectorParams() → 收集设备硬件参数
// 2. SetSelectorProperties() → 设置到匹配引擎
// 3. FindMatchingProfile() → 执行匹配
// 4. 返回 Profile 名称给引擎的 Device Profile 系统
```

### 编辑器设备预览

Editor 模块支持通过 ADB 导出已连接设备的参数为 JSON 文件：

```cpp
// 编辑器中导出连接设备的参数
FAndroidDeviceProfileSelectorModule Selector;
if (Selector.CanExportDeviceParametersToJson())
{
    FString OutputFolder = TEXT("/Engine/Content/Editor/PIEPreviewDeviceSpecs/Android");
    Selector.ExportDeviceParametersToJson(OutputFolder);
}

// 从 JSON 文件读取设备参数
TMap<FName, FString> DeviceParams;
FString JsonPath = TEXT("Samsung_GalaxyS24(OS14).json");
Selector.GetDeviceParametersFromJson(JsonPath, DeviceParams);
```

### ADB Commandlet

用于批量导出已连接 Android 设备的参数。以无限循环运行，自动检测新插入的设备：

```bash
# 命令行用法
UE5Editor.exe -run=AndroidDeviceDetection.CreateAndroidPreviewDataFromADB -ConfigRules="path/to/configrules.txt" -DeviceSpecsFolder="Engine/Content/Editor/PIEPreviewDeviceSpecs/Android"
```

参数说明：
- `-ConfigRules`：指向 `configrules.txt` 文件，用于根据 chipset 信息补充 GPU/Chipset 字段
- `-DeviceSpecsFolder`：JSON 输出目录

## Demo 示例

### 完整的自定义 Device Profile 设置流程

**第一步**：创建自定义 Device Profile（在项目或平台 `.ini` 中）

```ini
; Config/Android/DeviceProfiles.ini
[Android_SuperHigh @ Android]
r.MobileContentScaleFactor=1.0
r.MobileMaxFrameRate=60
r.Vulkan.EnableVulkanSM5=1

[Android_Medium @ Android]
r.MobileContentScaleFactor=0.85
r.MobileMaxFrameRate=30
r.Vulkan.EnableVulkanSM5=0
```

**第二步**：添加匹配规则

```ini
; Config/Android/DeviceProfiles.ini
[/Script/AndroidDeviceProfileSelector.AndroidDeviceProfileMatchingRules]
; 高端设备：Adreno 7xx/8xx + 8GB+ 内存 + Vulkan
+MatchProfile=(Profile="Android_SuperHigh",Match=((SourceType=SRC_GpuFamily,CompareType=CMP_Regex,MatchString="Adreno \\\\(TM\\\\) [7-8][0-9][0-9]"),(SourceType=SRC_TotalPhysicalGB,CompareType=CMP_GreaterEqual,MatchString="8"),(SourceType=SRC_VulkanAvailable,CompareType=CMP_Equal,MatchString="true")))

; 中端设备 fallback
+MatchProfile=(Profile="Android_Medium",Match=((SourceType=SRC_GpuFamily,CompareType=CMP_Regex,MatchString="Adreno \\\\(TM\\\\) [5-6][0-9][0-9]")))
```

**第三步**：构建并部署到设备，引擎日志（LogAndroid）会显示匹配过程：
```
LogAndroid: Checking 45 rules from DeviceProfile ini file.
LogAndroid:   Default profile: Android
LogAndroid:   SRC_GPUFamily: Adreno (TM) 740
LogAndroid:   SRC_AndroidVersion: 13
LogAndroid:   ...
LogAndroid: Selected Device Profile: [Android_SuperHigh]
```

## 模块依赖

### AndroidDeviceProfileSelector（Editor 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `AndroidDeviceDetection` | ADB 设备检测（仅 Editor，可禁用） |
| `PIEPreviewDeviceSpecification` | PIE 设备预览规格（仅 Editor） |
| `Json` / `JsonUtilities` | JSON 序列化（仅 Editor） |

### AndroidDeviceProfileSelectorRuntime（RuntimeNoCommandlet 模块）

| 模块 | 用途 |
|---|---|
| `Core` / `CoreUObject` | 核心基础库 |
| `Engine` | 引擎核心 |
| `AndroidDeviceProfileSelector` | 匹配规则引擎 |
| `HeadMountedDisplay` | VR 头显检测（获取 HMDSystemName） |

### AndroidDeviceProfileCommandlets（Editor 模块）

| 模块 | 用途 |
|---|---|
| `Core` / `CoreUObject` | 核心基础库 |
| `Engine` | 引擎核心 |
| `Json` / `JsonUtilities` | JSON 序列化 |
| `AndroidDeviceProfileSelector` | 匹配规则引擎 |
| `PIEPreviewDeviceSpecification` | PIE 设备预览规格 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-30 | `1bbf23339c41` | Remove direct access to UHT generated functions when UE_WITH_CONSTINIT_UOBJECT is true | 适配 UE5 的 constinit UObject 反射系统重构，使用早启动阶段的 constinit 反射信息替代动态生成的构造函数调用 |
| 2025-08-18 | `27d0289eff3f` | Add warning when no devices were found when attempting to export device parameters to json | 改善开发者体验：ADB 导出设备参数时如果没有检测到设备，现在会输出警告而非静默失败 |
| 2025-07-21 | `14aec604a3f7` | Add FAndroidMisc::GetVKQualityRecommendation() and SRC_VKQuality | 新增 Vulkan 质量推荐参数，允许匹配规则基于设备的 Vulkan 性能等级做更精细的画质决策 |

### 维护评价

- **年龄**：2014 年创建，已存在 12 年，是 UE Android 支持的基础设施之一
- **活跃度**：**活跃维护中** — 2025 年 7-9 月连续有功能性更新，包括新参数（VKQuality）和架构适配（constinit UObject）
- **稳定性**：核心匹配逻辑长期稳定，最近的改动主要是平台适配和增量改进
- **推荐度**：✅ **强烈推荐**。这是 UE5 Android 开发的必备插件，默认启用，无需额外操作。如果你需要为特定设备定制画质，只需在 `DeviceProfiles.ini` 中添加匹配规则即可

**注意事项**：
- 匹配规则的顺序至关重要——规则从上到下检查，第一个完全匹配的胜出
- 正则表达式匹配会将捕获组1存入 `SRC_PreviousRegexMatch`，可用于级联条件
- Hash 比较模式需要配置 `HASH_PEPPER_SECRET_GUID`，否则 Pepper 为空
- 模拟器检测在 Non-Shipping 构建中默认强制使用专用 Profile（可通过 `bForceEmulatorProfileSelectionInNonShippingBuilds` 配置控制）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidDeviceProfileSelector)
- [官方文档]()（无专用文档页）
- [匹配规则配置示例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Config/BaseDeviceProfiles.ini)（第 837-917+ 行）
