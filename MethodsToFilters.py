import Methods 
import Filters

methods_to_filters = {
	Methods.ListInterfaces: Filters.ListInterfaces_Filter,
	Methods.ResponderAnalyzeInterface: Filters.ResponderAnalyzeInterface_Filter,
	Methods.ArpScan: Filters.ArpScan_Filter,
	Methods.PortScan: Filters.PortScan_Filter,
	Methods.NBNSIPTranslation: Filters.NBNSIPTranslation_Filter,
	Methods.QueryRootDSEOfDCThroughLDAP: Filters.QueryRootDSEOfDCThroughLDAP_Filter,
	Methods.NBNSGroupMembers: Filters.NBNSGroupMembers_Filter,
	Methods.CheckIfSMBServiceIsRunning: Filters.CheckIfSMBServiceIsRunning_Filter,
	Methods.CheckIfMSRPCServiceIsRunning: Filters.CheckIfMSRPCServiceIsRunning_Filter,
	Methods.DumpInterfaceEndpointsFromEndpointMapper: Filters.DumpInterfaceEndpointsFromEndpointMapper_Filter,
	Methods.EnumDomainsThroughRPC: Filters.EnumDomainsThroughRPC_Filter,
	Methods.EnumDomainTrustsThroughRPC: Filters.EnumDomainTrustsThroughRPC_Filter,
	Methods.EnumDomainUsersThroughRPC: Filters.EnumDomUsersThroughRPC_Filter,
	Methods.EnumDomainGroupsThroughRPC: Filters.EnumDomGroupsThroughRPC_Filter
}