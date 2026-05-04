# DMX Control Console

> Console that can be patched from DMX Libraries and sends DMX to Output Ports

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXControlConsole` (Runtime), `DMXControlConsoleEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole) | |

## 用途

DMX Control Console 是一个虚拟 DMX 控制台插件，为 Unreal Engine 的虚拟制片工作流提供实时 DMX 通道控制能力。它解决的核心问题是：**在编辑器内提供一个可视化的 DMX 调光台界面，让用户可以直接操控 DMX 通道值并实时发送到物理灯光设备**。

该插件的工作流程如下：
1. 从 DMX Library（DMX 库）中加载已配置的灯具 Patch（补丁/映射）
2. 将 Patch 自动或手动组织为 Fader Group（推杆组），每组对应一个灯具或一组通道
3. 通过 Fader（推杆/滑块）实时调整 DMX 通道值（0-255）
4. 将调整后的 DMX 数据通过 Output Port（输出端口）发送到 Art-Net / sACN 等 DMX 网络

与传统的外部 DMX 控制台软件不同，此插件直接嵌入编辑器，可以与 Sequencer、蓝图、nDisplay 等 UE 虚拟制片工具无缝配合。

## 使用场景

- 你在搭建虚拟制片场景，需要在编辑器内实时调整灯光的 DMX 参数 → 用 DMX Control Console
- 你需要快速测试 DMX Library 中配置的灯具 Patch 是否正确 → 用 DMX Control Console 的 Fader 界面逐通道验证
- 你在用 nDisplay + DMX 控制实际舞台灯光，需要一个内嵌的调光台 → 用 DMX Control Console
- 你需要保存和加载不同的 DMX 控制台配置（不同场景不同灯光布局）→ 用 DMX Control Console Asset

## 蓝图用法

> ⚠️ 本插件主要面向编辑器 UI 操作，蓝图 API 较少。核心交互通过编辑器 Widget 完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetControlConsoleCategory` | 获取 Control Console 资产在编辑器中的分类路径 | `IDMXControlConsoleEditorModule` |

### 使用示例（蓝图描述）

本插件的使用主要通过编辑器 UI 面板完成，而非蓝图节点。典型工作流：

1. 打开 **Window > Virtual Production > DMX Control Console** 面板
2. 在面板中选择 DMX Library，自动加载已配置的 Fixture Patch
3. 使用 Fader 滑块实时调整各通道 DMX 值
4. 通过工具栏按钮保存/加载 Console Asset

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块接口
#include "IDMXControlConsoleEditorModule.h"
```

### 基本用法

获取编辑器模块实例并查询资产分类：

```cpp
// 来源: IDMXControlConsoleEditorModule.h
#include "IDMXControlConsoleEditorModule.h"

// 获取 DMX Control Console 编辑器模块
IDMXControlConsoleEditorModule& ConsoleModule = IDMXControlConsoleEditorModule::Get();

// 获取 Control Console 资产的分类路径（用于 Content Browser 分类显示）
FAssetCategoryPath Category = ConsoleModule.GetControlConsoleCategory();
```

### 进阶用法

在自定义编辑器扩展中注册 DMX Control Console 资产分类：

```cpp
#include "IDMXControlConsoleEditorModule.h"
#include "AssetRegistry/AssetData.h"

void FMyEditorExtension::RegisterAssetCategory()
{
    if (FModuleManager::Get().IsModuleLoaded("DMXControlConsoleEditor"))
    {
        IDMXControlConsoleEditorModule& ConsoleModule = IDMXControlConsoleEditorModule::Get();
        
        // 获取 Control Console 资产分类，用于在自定义 UI 中过滤资产
        FAssetCategoryPath ConsoleCategory = ConsoleModule.GetControlConsoleCategory();
        
        // 可用于 Content Browser 过滤器或自定义资产选择器
        UE_LOG(LogTemp, Log, TEXT("DMX Control Console Category: %s"), *ConsoleCategory.ToString());
    }
}
```

## 模块架构

本插件包含两个模块，共约 253 个源文件，属于 **xlarge** 规模插件。

### DMXControlConsole（Runtime）

核心运行时模块，包含：

| 子系统 | 说明 |
|---|---|
| **数据模型** | Fader Group、Fader、Patch 等核心数据结构 |
| **控制器** | DMXControlConsoleController — 管理控制台状态和 DMX 输出 |
| **资产类型** | UDMXControlConsoleAsset — 可序列化的控制台配置 |
| **DMX 输出** | 通过 Output Port 发送 DMX 数据到 Art-Net/sACN |

### DMXControlConsoleEditor（Runtime）

编辑器 UI 模块（类型为 Runtime 以支持 nDisplay 等运行时编辑器场景），包含：

| 子系统 | 说明 |
|---|---|
| **主面板 Widget** | DMX Control Console 编辑器面板 |
| **Fader Strip Widget** | 单个灯具/通道组的推杆条 UI |
| **Patch 管理 UI** | 从 DMX Library 选择和组织 Patch |
| **工具栏扩展** | 保存/加载/自动分组等工具栏按钮 |
| **资产分类** | 在 Content Browser 中注册 Control Console 资产分类 |

## Demo 示例

### 自定义编辑器扩展集成

```cpp
// MyDMXExtension.h
#pragma once

#include "CoreMinimal.h"

class FMyDMXExtension
{
public:
    /** 初始化 DMX Control Console 集成 */
    void Initialize();
    
    /** 检查 DMX Control Console 模块是否可用 */
    bool IsConsoleAvailable() const;
    
    /** 获取控制台资产分类路径 */
    FAssetCategoryPath GetConsoleAssetCategory() const;
};
```

```cpp
// MyDMXExtension.cpp
#include "MyDMXExtension.h"
#include "IDMXControlConsoleEditorModule.h"

void FMyDMXExtension::Initialize()
{
    // 确保 DMX Control Console 编辑器模块已加载
    if (!FModuleManager::Get().IsModuleLoaded("DMXControlConsoleEditor"))
    {
        FModuleManager::Get().LoadModule("DMXControlConsoleEditor");
    }
}

bool FMyDMXExtension::IsConsoleAvailable() const
{
    return FModuleManager::Get().IsModuleLoaded("DMXControlConsoleEditor");
}

FAssetCategoryPath FMyDMXExtension::GetConsoleAssetCategory() const
{
    if (IsConsoleAvailable())
    {
        return IDMXControlConsoleEditorModule::Get().GetControlConsoleCategory();
    }
    return FAssetCategoryPath{};
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXRuntime` | DMX 协议核心运行时（Art-Net/sACN 通信、DMX 数据帧） |
| `DMXEditor` | DMX Library 和 Fixture Patch 编辑功能 |

> 无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- e803ea92e532 DMX: Fix Control Console updates slowly when changing auto-grouped patches in auto mode
  → 修复自动模式下切换自动分组 Patch 时控制台更新缓慢的问题
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
  → 代码质量改进：移除 FORCEINLINE 宏，改用 inline
- 4e85e0cfc90d DMX: Fix an issue where newly added patches cannot be used in control console when created while the control console was not loaded
  → 修复在控制台未加载时新建的 Patch 无法在控制台中使用的问题
```

### 维护评价

- **创建时间**：2023 年 3 月，属于较新的插件（约 2 年）
- **维护状态**：**活跃维护中** — 近期 commit 均为实质性 bug 修复和性能优化
- **稳定性**：已标记为非 Beta（IsBetaVersion=false），处于正式发布状态
- **已知限制**：
  - 需要配合 DMX 插件体系使用（DMXRuntime、DMXEditor）
  - 编辑器模块类型为 Runtime，这是为了支持 nDisplay 等需要运行时编辑器功能的场景
- **推荐程度**：✅ **推荐使用** — 如果你的虚拟制片工作流需要在编辑器内实时控制 DMX 灯光，这是官方提供的标准解决方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole)
- [DMX 插件体系](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX)