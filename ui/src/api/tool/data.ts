import {PageResult} from "../PageResult";

export interface ToolPageResult extends PageResult{
    items: ToolResult[]
}

export interface ToolPayload {
    configuration: any
    [key: string]: any
}

export interface ToolCreatePayload extends ToolPayload {
    name: string
    title: string
    description: string
    model_id: string
}

export interface ToolUpdatePayload extends ToolPayload {
    id: string
    title: string
    description: string
    model_id: string
}

export interface ToolResult {
    id: any
    name: string
    title: string
    description: string
    is_system: boolean
    configuration: any
    model_id: string
}

export enum ToolFieldType {
    STRING = "string",
    NUMBER = "number",
    INTEGER = "integer",
    BOOLEAN = "boolean"
}

export interface ToolFieldDefinition {
    type: ToolFieldType
    default: string
}

export interface ToolProperties {
    [field: string]: ToolFieldDefinition
}

export interface ToolFields {
    properties: ToolProperties
}

export interface ToolConfigurationFields {
    name: string
    fields: ToolFields
}
