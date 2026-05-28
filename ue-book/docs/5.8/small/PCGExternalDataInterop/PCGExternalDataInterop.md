# Procedural Content Generation Framework (PCG) External Data Interop

> Extra plugin for Procedural Content Generation Framework interacting with external data formats.

| 属性 | 值 |
|---|---|
| 中文名 | PCG外部数据互通 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGExternalDataInterop` (Runtime), `PCGExternalDataInteropEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGExternalDataInterop) | |

## 用途

PCGExternalDataInterop 是 PCG（程序化内容生成框架）与外部数据格式之间的桥梁插件。它解决的核心问题是：**如何将外部存储的几何数据（如 Alembic .abc 文件）导入到 PCG 图表中作为程序化生成的输入数据**。

Alembic 是影视和游戏行业广泛使用的开放标准几何缓存格式（`.abc`），用于存储动画网格、点云、粒子等数据。该插件让关卡设计师和程序化内容艺术家能够：
- 直接在 PCG 图表中加载 `.abc` 文件
- 自动处理不同 DCC 工具（3ds Max、Maya）的坐标系差异
- 将 Alembic 数据转换为 PCG 可用的点云/属性数据

## 使用场景

- 你有一个从 Houdini 导出的建筑分布点云 `.abc` 文件，需要在 UE 中程序化生成建筑 → 用 PCG + LoadAlembic 节点
- 你的艺术团队从 Maya 或 3ds Max 导出了带有位置/旋转信息的几何缓存 → 用预设的坐标转换（CitySample 或自定义）
- 你需要将外部工具生成的程序化数据导入 PCG 流程，而非手动摆放 → 用该插件作为数据桥梁

## 蓝图用法

该插件主要作为 PCG 图表中的节点使用，核心交互 API 在 `UPCGLoadAlembicSettings` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupFromStandard` | 根据预设标准（如 CitySample）快速配置导入参数 | `UPCGLoadAlembicSettings` |

### PCG 图表节点

在 PCG 图表编辑器中，该插件提供以下节点：

| 节点名 | 说明 |
|---|---|
| `LoadAlembic` | 从 `.abc` 文件加载几何数据到 PCG 点云 |

### LoadAlembic 节点属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `AlembicFilePath` | FilePath | Alembic 文件路径（支持 .abc 文件过滤） |
| `ConversionScale` | FVector | 导入时的缩放比例，默认 (1, -1, 1) 翻转 Y 轴 |
| `ConversionRotation` | FVector | 导入时的欧拉角旋转，3ds Max 用 (90, 0, 0) |
| `bConversionFlipHandedness` | bool | 翻转旋转方向，配合坐标交换使用 |
| `Setup` | Enum | 一键应用预设配置（仅编辑器可见） |

### 使用示例（蓝图描述）

1. 在 PCG 图表中，右键搜索并添加 **LoadAlembic** 节点
2. 在节点详情面板中，点击 **AlembicFilePath** 选择 `.abc` 文件
3. 如果数据来自 **Maya**：保持默认缩放 (1, -1, 1)
4. 如果数据来自 **3ds Max**：设置旋转为 (90, 0, 0)
5. 或者点击 **Setup from standard** 下拉选择 **CitySample** 预设，自动配置所有参数
6. 将 LoadAlembic 节点的输出连接到下游的生成/变换节点

## C++ 用法

### 头文件引入

```cpp
#include "Elements/PCGLoadAlembicElement.h"
```

### 基本用法

使用预设配置快速设置 Alembic 导入参数：

```cpp
// 创建 LoadAlembic 设置对象
UPCGLoadAlembicSettings* Settings = NewObject<UPCGLoadAlembicSettings>();

// 方法一：使用 CitySample 预设（自动配置坐标系、缩放、旋转等）
Settings->SetupFromStandard(EPCGLoadAlembicStandardSetup::CitySample);

// 方法二：手动配置（适用于自定义 DCC 工具）
Settings->AlembicFilePath.FilePath = TEXT("C:/Assets/pointcloud.abc");
Settings->ConversionScale = FVector(1.0f, -1.0f, 1.0f);   // 翻转 Y 轴
Settings->ConversionRotation = FVector(90.0f, 0.0f, 0.0f); // 3ds Max 旋转修正
Settings->bConversionFlipHandedness = true;
```

### 进阶用法

静态方法形式调用，适用于需要在不同上下文中复用配置逻辑：

```cpp
// 使用静态版本，直接传入参数引用
FVector Scale = FVector::OneVector;
FVector Rotation = FVector::ZeroVector;
bool bFlipHandedness = false;
TMap<FString, FPCGAttributePropertyInputSelector> AttributeMapping;

// 应用 CitySample 预设到现有变量
UPCGLoadAlembicSettings::SetupFromStandard(
    EPCGLoadAlembicStandardSetup::CitySample,
    Scale,
    Rotation,
    bFlipHandedness,
    AttributeMapping
);

// 此时 Scale/Rotation/bFlipHandedness/AttributeMapping 已被修改为 CitySample 预设值
// AttributeMapping 包含了 orient→rotation 和 scale→scale 的属性映射关系
```

## Demo 示例

一个最小化的自定义 PCG 节点，基于 LoadAlembic 的设置类扩展：

```cpp
// MyCustomAlembicNode.h
#pragma once

#include "Elements/PCGLoadAlembicElement.h"
#include "MyCustomAlembicNode.generated.h"

UCLASS(MinimalAPI, BlueprintType, ClassGroup = (Procedural))
class UMyCustomAlembicNodeSettings : public UPCGLoadAlembicSettings
{
    GENERATED_BODY()

public:
#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override { return FName(TEXT("MyCustomAlembic")); }
    virtual FText GetDefaultNodeTitle() const override
    {
        return NSLOCTEXT("PCG", "MyCustomAlembic", "My Custom Alembic Loader");
    }
#endif

protected:
    virtual FPCGElementPtr CreateElement() const override;

    // 自定义属性：额外的过滤条件
    UPROPERTY(EditAnywhere, Category = "Filter")
    float MinPointDistance = 0.0f;
};
```

```cpp
// MyCustomAlembicNode.cpp
#include "MyCustomAlembicNode.h"

FPCGElementPtr UMyCustomAlembicNodeSettings::CreateElement() const
{
    return MakeShared<FPCGLoadAlembicElement>();
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `PCGFramework` | PCG 核心框架，提供 UPCGSettings、FPCGElement 等基类 |
| `PCGExternalDataInterop` | 外部数据互通基础模块（Editor 模块依赖 Runtime 模块） |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-01-09 | `49c11077` | [UObject] | UObject 相关维护更新 |
| 2025-09-23 | `e22e769b` | [PCG] Better management of windows headers wrt alembic files | 改善 Windows 头文件与 Alembic 的兼容性 |
| 2025-09-23 | `68b1d8a9` | [PCG] Moved code to implementation file for better isolation. Also removed GetObject define that cou | 代码移至实现文件以隔离依赖，修复 GetObject 宏冲突 |
| 2025-05-14 | `6bd1bdeb` | Fix compile error because winnt.h is included by Alembic includes, which redefines MemoryBarrier, th | 修复 winnt.h 与 Alembic 头文件的 MemoryBarrier 宏冲突编译错误 |

### 维护评价

**维护状态：活跃维护中** ✅

- 该插件创建于 2024 年 8 月，年龄约 2 年，属于较新的插件
- 版本号 0.2，仍处于早期迭代阶段
- 近期更新集中在**平台兼容性修复**（Windows 头文件冲突、Alembic 依赖隔离），说明插件在持续被使用和打磨
- 多次修复 Alembic 头文件与 Windows 系统头文件的宏冲突，这是 Alembic 集成的常见痛点
- 2026 年仍有更新，表明 Epic 将其作为 PCG 生态的活跃组件维护
- **推荐使用**：如果你的 PCG 工作流需要导入外部几何数据（特别是 Alembic 格式），这是官方推荐的数据互通方案。注意版本号仍为 0.2，API 可能在未来版本中有变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGExternalDataInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGExternalDataInterop/Tests)（如有）