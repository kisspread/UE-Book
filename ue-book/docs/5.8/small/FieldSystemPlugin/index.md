# Field System

> Analytic Field

| 属性 | 值 |
|---|---|
| 中文名 | 场系统编辑器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（FieldSystem 资产、编辑器图标） |
| 模块 | `FieldSystemEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-12-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FieldSystemPlugin) | |

## 用途

FieldSystemPlugin 提供了 **Field System（场系统）** 资产的编辑器支持，用于创建和管理分析场（Analytic Field）资产。Field System 是 Unreal Engine 物理系统的一部分，主要服务于 Chaos Destruction（混沌破碎）系统，允许开发者定义空间中的标量/向量场，用于控制破碎模拟中的力、速度、破碎程度等物理属性的空间分布。

该插件本身是一个纯编辑器插件（尽管模块类型标记为 Runtime），负责：
- 注册 FieldSystem 资产类型及其在内容浏览器中的展示
- 提供 FieldSystem 资产的创建工厂
- 处理 FieldSystem Actor 的生成逻辑
- 定义编辑器中使用的类图标和缩略图样式

## 使用场景

- 你需要对 Chaos Destruction 破碎效果进行空间化控制 → 定义 Field System 来指定不同区域的破碎强度
- 你需要创建受力场影响粒子、刚体等物理对象 → 使用 Field System 定义力的空间分布
- 你需要在编辑器中可视化和编辑物理场 → 通过该插件提供的资产编辑器操作 Field System

## 蓝图用法

该插件主要提供编辑器资产类型支持，不直接暴露蓝图可调用函数。FieldSystem 资产在编辑器中创建后，通常由 Chaos Destruction 系统在运行时使用。

### 核心资产操作

| 操作 | 说明 |
|---|---|
| 创建 Field System 资产 | 在内容浏览器中右键 → Physics → Field System |
| 拖放到场景 | 自动创建 FieldSystem Actor |

## C++ 用法

该插件是编辑器扩展，C++ 用法集中在资产类型注册和工厂模式。

### 头文件引入

```cpp
#include "Field/FieldSystemEditorModule.h"
#include "Field/FieldSystemFactory.h"
```

### 基本用法

检查 FieldSystemEditor 模块是否可用：

```cpp
// Source: Source/FieldSyStemEditor/Public/Field/FieldSystemEditorModule.h
if (IFieldSystemEditorModule::IsAvailable())
{
    IFieldSystemEditorModule& EditorModule = IFieldSystemEditorModule::Get();
}
```

### 工厂创建

```cpp
// Source: Source/FieldSyStemEditor/Public/Field/FieldSystemFactory.h
// 通过工厂创建新的 FieldSystem 资产
UFieldSystem* NewFieldSystem = Cast<UFieldSystem>(
    UFieldSystemFactory::StaticFactoryCreateNew(
        UFieldSystem::StaticClass(),
        InPackage,
        FName("MyFieldSystem"),
        RF_Public | RF_Standalone,
        nullptr,
        GWarn
    )
);
```

## Demo 示例

该插件为编辑器扩展，不包含运行时示例代码。典型使用方式是：

1. 在编辑器中启用插件（Edit → Plugins → Field System）
2. 在内容浏览器中右键 → 创建 Physics → Field System 资产
3. 编辑 Field System 资产中的场定义
4. 将 Field System 资产拖放到场景中或关联到 Chaos Destruction Actor

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复重复符号链接错误 |
| 2023-11-15 | `b64f2e25` | [Deprecation Cleanup] Remove deprecated code in actor factory class | 清理 ActorFactory 中的废弃代码 |
| 2023-02-17 | `73c74eaf` | Removing redundant include paths: | 移除冗余的 include 路径 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量更新 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件链接为安全协议 |

### 维护评价

⚠️ **该插件长期处于实验性状态，建议谨慎使用。**

- **创建时间**：2018年12月，至今已约7年
- **状态**：IsBetaVersion = true，EnabledByDefault = false，仍在 Experimental 目录
- **更新频率**：近年来仅有零散的维护性提交（编译修复、废弃代码清理），无功能性更新
- **源码规模**：极小（11个文件），功能有限，主要提供编辑器资产类型注册
- **注意**：该插件是 Chaos Destruction 系统的编辑器侧支持的一部分，核心 FieldSystem 运行时功能可能在其他模块中实现

**建议**：如果你只需要 FieldSystem 的运行时功能（如在 Chaos Destruction 中使用），该插件可能不是必需的。如果你需要在编辑器中创建和管理 FieldSystem 资产，需手动启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FieldSystemPlugin)
- [官方文档]()（无）