# Alembic Groom Importer

> Import Hair Strands from Alembic file

| 属性 | 值 |
|---|---|
| 中文名 | Alembic 毛发导入器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicHairTranslatorModule` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter) | |

## 用途

该插件为 Unreal Engine 提供从 Alembic（`.abc`）文件导入毛发数据（Groom / Hair Strands）的能力。它通过实现 `IGroomTranslator` 接口，将 Alembic 文件中的毛发曲线数据转换为引擎内部的 `FHairDescription` 结构，供 HairStrands 渲染系统使用。

该插件**默认未启用**，需要在项目设置中手动启用，同时依赖 HairStrands 插件。它是一个纯编辑器插件（不参与运行时），仅在导入流程中发挥作用。

## 使用场景

- 你从 Blender、Houdini、XGen 等 DCC 工具导出了毛发造型（Alembic 格式），需要导入 UE5 中使用 Groom 系统渲染
- 你需要导入包含毛发动画的 Alembic 文件（多帧 Groom 动画）
- 你的项目使用了 HairStrands 毛发渲染方案，需要从外部资产导入毛发数据

**前置条件**：
1. 启用 `HairStrands` 插件
2. 启用 `AlembicHairImporter` 插件

## 蓝图用法

该插件不暴露任何蓝图可调用函数。它是一个纯编辑器导入器，仅通过编辑器的 **Import** 流程（Content Browser → Import）或 **Groom 资产**的导入界面工作，无法在运行时蓝图中调用。

## C++ 用法

该插件的核心是一个 `IGroomTranslator` 接口的实现类 `FAlembicHairTranslator`，由模块在启动时注册到 Groom 导入管线中。使用者通常无需直接调用其 C++ API，而是在编辑器中通过 UI 导入。

### 核心类

```cpp
// 私有头文件，仅供插件内部使用
class FAlembicHairTranslator : public IGroomTranslator
{
public:
    // 静态导入：一次性翻译整个文件
    virtual bool Translate(const FString& FilePath, FHairDescription& OutHairDescription,
                           const FGroomConversionSettings& ConversionSettings) override;

    // 判断是否可以翻译该文件
    virtual bool CanTranslate(const FString& FilePath) override;

    // 判断文件扩展名是否受支持
    virtual bool IsFileExtensionSupported(const FString& FileExtension) const override;

    // 返回支持的文件格式描述
    virtual FString GetSupportedFormat() const override;

    // 带动画信息的导入
    virtual bool Translate(const FString& FilePath, FHairDescription& OutHairDescription,
                           const FGroomConversionSettings& ConversionSettings,
                           FGroomAnimationInfo* OutAnimInfo) override;

    // 逐帧导入（动画支持）
    virtual bool BeginTranslation(const FString& FilePath) override;
    virtual bool Translate(float FrameTime, FHairDescription& OutHairDescription,
                           const FGroomConversionSettings& ConversionSettings) override;
    virtual void EndTranslation() override;
};
```

### 头文件引入

由于该插件是 Editor-only 且类为私有实现，外部模块通常不需要直接引入其头文件。如果需要在自定义导入管线中使用：

```cpp
#include "GroomTranslator.h"  // IGroomTranslator 接口（来自 HairStrands 模块）
```

## Demo 示例

该插件没有公开的可直接使用的 C++ API，以下展示的是在编辑器中导入 Alembic 毛发的标准流程：

1. 在 Content Browser 中右键 → **Import**
2. 选择 `.abc` 文件（包含毛发曲线数据）
3. 导入器自动识别文件格式并调用 `FAlembicHairTranslator::Translate()`
4. 生成 **Groom** 资产，可在 Skeletal Mesh 上绑定使用

如果需要通过代码触发导入（高级用法）：

```cpp
// 通常不需要直接这样做，编辑器 UI 已覆盖此流程
// 以下为示意性代码，展示 IGroomTranslator 的使用模式
#include "GroomTranslator.h"

void ImportGroomFromAlembic(const FString& AbcFilePath, const FGroomConversionSettings& Settings)
{
    // 插件注册后，Groom 导入管线会自动选择合适的 Translator
    // 外部代码通过 FHairDescription 获得结果即可
    FHairDescription HairDescription;
    
    // IGroomTranslator 实例由 GroomImportSubsystem 管理
    // 通常不直接实例化 FAlembicHairTranslator
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrands` | 毛发渲染核心模块，提供 FHairDescription、IGroomTranslator 等基础类型 |
| `GeometryCache` | Alembic 文件解析支持（通过 Alembic 库读取毛发曲线数据） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新日志格式 |
| 2024-05-03 | `1fde5666` | PR #10617: AlembicHairImporterFixes: RootUV from Blender Hair / no RootUV registration when not pars | 修复 Blender 毛发 RootUV 导入及未解析时不注册 RootUV 的问题 |
| 2024-04-16 | `96a33f78` | Fixed potential uninitialized FVectors in AlembicHairImporter. | 修复导入器中 FVector 可能未初始化的问题 |
| 2023-10-13 | `ba50d6b0` | Alembic: Fix import issues with corrupted Alembic files. | 修复损坏的 Alembic 文件导入失败的问题 |
| 2023-08-08 | `bdb4199e` | Remove unnecessary WindowsHWrapper.h & MinWindows.h include - both files will be automatically inclu | 移除不必要的 Windows 平台头文件引用 |

### 维护评价

- **创建时间**：2020 年 11 月，约 5 年历史
- **最近更新**：最近一次功能性修复在 2024 年 5 月（RootUV 问题），2026 年的更新仅为日志宏迁移
- **维护状态**：**维护中**——作为 Alembic 毛发导入的核心组件，偶尔收到 bug 修复，但更新频率较低
- **已知限制**：
  - 默认未启用，需要手动激活
  - 依赖 HairStrands 插件
  - 不支持运行时动态导入（纯编辑器功能）
  - 仅 4 个源文件，功能边界清晰但扩展性有限
- **推荐使用**：如果你需要从 DCC 工具导入 Alembic 格式的毛发数据到 UE5 HairStrands 系统，这是**必须使用**的插件，没有替代方案。建议启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicHairImporter)
- 官方文档：无（.uplugin 中 DocsURL 为空）