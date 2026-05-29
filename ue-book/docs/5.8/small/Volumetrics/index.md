# Volumetrics

> A library of volume creation and rendering tools using Blueprints.

| 属性 | 值 |
|---|---|
| 中文名 | 体积渲染库 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、着色器） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2019-10-18 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Volumetrics) | |

## 用途

这是一个**纯内容插件**，提供基于蓝图的体积效果创建和渲染工具库。插件原本包含 C++ 代码，但在 2021 年被移除代码并转换为纯内容插件，仅保留蓝图资产、材质和着色器资源。

插件依赖三个关键插件协同工作：
- **BlueprintMaterialTextureNodes**：提供蓝图中的材质和纹理操作节点
- **Landmass**：提供地形相关的体积效果支持
- **Niagara**：提供粒子系统的体积渲染能力

该插件用于创建各种体积渲染效果，如雾气、云层、大气散射等体积视觉效果，主要面向需要快速搭建体积渲染原型的场景。

## 使用场景

- 你需要在场景中快速创建逼真的体积雾效果 → 用 Volumetrics
- 你需要基于蓝图的云层或大气体积渲染方案 → 用 Volumetrics
- 你需要与 Niagara 粒子系统结合的体积效果 → 用 Volumetrics
- 你需要地形相关的体积渲染效果（如低洼雾气） → 用 Volumetrics + Landmass

## 蓝图用法

由于本插件是纯内容插件，没有自定义 C++ 模块，因此不提供自定义蓝图节点。蓝图资产本身作为预构建的体积效果模板供用户直接使用或作为参考。

### 核心资产

插件通过内容资产提供以下能力（资产具体名称需在编辑器中查看 Content Browser）：
- 体积效果蓝图模板
- 配套材质和材质实例
- 着色器文件

### 使用示例（蓝图描述）

1. 在 Content Browser 中导航到 `/Volumetrics/` 目录
2. 浏览可用的蓝图资产和材质
3. 将蓝图资产拖拽到场景中使用，或作为参考创建自定义体积效果
4. 根据需要调整材质参数和蓝图属性

## C++ 用法

本插件不包含 C++ 代码模块，无法直接在 C++ 中使用。如需在 C++ 项目中使用类似功能，可参考插件提供的材质和着色器进行移植。

## Demo 示例

本插件为纯内容插件，无 C++ 代码示例。使用方式为直接在编辑器中使用提供的蓝图资产和材质资源。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

**插件依赖**：

| 插件 | 用途 |
|---|---|
| `BlueprintMaterialTextureNodes` | 蓝图中的材质和纹理操作节点 |
| `Landmass` | 地形相关体积效果支持 |
| `Niagara` | 粒子系统体积渲染能力 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-07-31 | `5f38a323` | Add Niagara as an explicit dependency to avoid illegal asset reference errors | 添加 Niagara 显式依赖以避免资产引用错误 |
| 2023-11-28 | `6d654177` | Add missing copyright boilerplate to shader files | 为着色器文件补充缺失的版权声明 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议 |
| 2021-04-27 | `8aa8d3e0` | Removing code from Volumetrics plugin and converted it to a content only plugin. Removed old volume | 移除插件代码，转换为纯内容插件 |
| 2020-10-29 | `68150e0b` | Merge UE5/Release-Engine-Staging to UE5/Main @ 14611496 | 合并引擎发布分支到主分支 |

### 维护评价

- **插件状态**：该插件已被**主动简化**——2021 年移除了所有 C++ 代码，转为纯内容插件，说明 Epic 认为体积渲染功能更适合通过蓝图和材质实现
- **维护频率**：更新频率较低，最近一次实质性更新（添加依赖）在 2024 年，其余多为维护性修改
- **实验性状态**：虽然位于 Experimental 目录，但 `.uplugin` 中 `IsBetaVersion` 为 false
- **依赖风险**：依赖 Niagara 和 Landmass 两个插件，增加了维护复杂度
- **推荐程度**：⚠️ 谨慎使用。该插件功能有限且更新不频繁，适合作为学习参考，但不建议作为核心项目的生产依赖。考虑直接使用 Niagara 和标准材质系统构建自定义体积效果方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Volumetrics)
- 官方文档：无