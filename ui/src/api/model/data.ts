import {PageResult} from "../PageResult";

export interface ModelPageResult extends PageResult {
    items: ModelResult[]
}

export interface ModelPayload {
    configuration: any
    [key: string]: any
}

export interface ModelCreatePayload extends ModelPayload {
    name: string
    title: string
    description: string
}

export interface ModelUpdatePayload extends ModelPayload {
    id: string
    title: string
    description: string
}

export interface ModelResult {
    id: any
    name: string
    title: string
    description: string
    is_system: boolean
    configuration: any
}

export enum ModelFieldType {
    STRING = "string",
    NUMBER = "number",
    INTEGER = "integer",
    BOOLEAN = "boolean"
}

export interface ModelFieldDefinition {
    type: ModelFieldType
    default: string
}

export interface ModelProperties {
    [field: string]: ModelFieldDefinition
}

export interface ModelFields {
    properties: ModelProperties
}

export interface ModelConfigurationFields {
    name: string
    fields: ModelFields
}
